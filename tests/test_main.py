"""Raspberry Pi Pico起動シーケンスの実機なし自動テスト。

関連設計ID: DESN-SW-003, DESN-SW-005, DESN-SW-006, DESN-SW-008
"""

import importlib
import sys
import types

import pytest

from pwm_controller import duty_u16_for


class FakePin:
    """machine.Pinを模擬するテスト用端子。

    関連設計ID: DESN-SW-005
    """

    IN = 0
    OUT = 1
    PULL_UP = 2
    input_values = {}
    instances = []
    read_error = None

    def __init__(self, pin_id, mode=None, pull=None):
        self.pin_id = pin_id
        self.mode = mode
        self.pull = pull
        self.history = []
        self.__class__.instances.append(self)

    def value(self):
        if self.__class__.read_error is not None:
            raise self.__class__.read_error
        return self.__class__.input_values.get(self.pin_id, 1)

    def on(self):
        self.history.append("点灯")

    def off(self):
        self.history.append("消灯")


class FakePwm:
    """machine.PWMを模擬するテスト用PWM。

    関連設計ID: DESN-SW-005
    """

    instances = []

    def __init__(self, pin):
        self.pin = pin
        self.frequency_history = []
        self.duty_history = []
        self.deinitialized = False
        self.__class__.instances.append(self)

    def freq(self, frequency):
        self.frequency_history.append(frequency)

    def duty_u16(self, duty):
        self.duty_history.append(duty)

    def deinit(self):
        self.deinitialized = True


@pytest.fixture
def main_module(monkeypatch):
    """machineとutimeを差し替えてmainを読み込む。

    関連設計ID: DESN-SW-005
    """
    FakePin.input_values = {1: 1, 2: 1, 3: 1, 4: 1}
    FakePin.instances = []
    FakePin.read_error = None
    FakePwm.instances = []

    machine_module = types.ModuleType("machine")
    machine_module.Pin = FakePin
    machine_module.PWM = FakePwm
    utime_module = types.ModuleType("utime")
    utime_module.sleep = lambda _seconds: None
    monkeypatch.setitem(sys.modules, "machine", machine_module)
    monkeypatch.setitem(sys.modules, "utime", utime_module)
    sys.modules.pop("main", None)

    module = importlib.import_module("main")
    yield module
    sys.modules.pop("main", None)


def test_module_startup_initializes_zero_percent(main_module):
    """モジュール起動時に起動表示後、入力0でLED点灯と0%を維持する。

    関連テストID: TEST-DESN-004, TEST-DESN-006
    """
    main_module.run(FakePin, FakePwm, lambda _seconds: None)
    pwm = FakePwm.instances[-1]
    input_pins = [pin for pin in FakePin.instances if pin.pin_id in (1, 2, 3, 4)]

    assert [(pin.pin_id, pin.mode, pin.pull) for pin in input_pins] == [
        (1, FakePin.IN, FakePin.PULL_UP),
        (2, FakePin.IN, FakePin.PULL_UP),
        (3, FakePin.IN, FakePin.PULL_UP),
        (4, FakePin.IN, FakePin.PULL_UP),
    ]
    assert pwm.pin.pin_id == 0
    assert pwm.frequency_history == [50, 50]
    assert pwm.duty_history == [0, 0]
    led = [pin for pin in FakePin.instances if pin.pin_id == 25][-1]
    assert led.history == ["消灯", "点灯", "消灯", "消灯", "消灯", "点灯"]


def test_run_applies_valid_switch_value(main_module):
    """設定値7を7回通知して70%へ設定する。

    関連テストID: TEST-SPEC-001, TEST-DESN-004
    """
    FakePin.input_values = {1: 0, 2: 0, 3: 0, 4: 1}
    sleep_history = []

    pwm = main_module.run(FakePin, FakePwm, sleep_history.append)
    led = [pin for pin in FakePin.instances if pin.pin_id == 25][-1]

    assert led.history.count("点灯") == 9
    assert led.history[-1] == "点灯"
    assert sleep_history == [0.5, 1] + [0.25] * 14 + [1]
    assert pwm.duty_history == [0, duty_u16_for(70)]


def test_run_applies_safe_output_for_invalid_switch_value(main_module):
    """設定値15を15回通知して0%へ設定する。

    関連テストID: TEST-SPEC-005, TEST-DESN-004
    """
    FakePin.input_values = {1: 0, 2: 0, 3: 0, 4: 0}
    sleep_history = []

    pwm = main_module.run(FakePin, FakePwm, sleep_history.append)
    led = [pin for pin in FakePin.instances if pin.pin_id == 25][-1]

    assert led.history.count("点灯") == 17
    assert led.history[-1] == "点灯"
    assert sleep_history == [0.5, 1] + [0.25] * 30 + [1]
    assert pwm.duty_history == [0, 0]


def test_run_sets_gp0_high_for_100_percent(main_module):
    """設定値10ではPWMを停止し、GP0を固定Highへ設定する。

    関連テストID: TEST-SPEC-001, TEST-DESN-004
    """
    FakePin.input_values = {1: 1, 2: 0, 3: 1, 4: 0}

    pwm = main_module.run(FakePin, FakePwm, lambda _seconds: None)
    output_pin = [pin for pin in FakePin.instances if pin.pin_id == 0][-1]

    assert pwm.deinitialized is True
    assert pwm.duty_history == [0]
    assert output_pin.history == ["点灯"]


def test_run_makes_output_safe_when_input_read_fails(main_module):
    """入力読取り例外時にPWMを0%へ戻してLEDを消灯する。

    関連テストID: TEST-DESN-010
    """
    FakePin.read_error = RuntimeError("入力読取り失敗")

    with pytest.raises(RuntimeError, match="入力読取り失敗"):
        main_module.run(FakePin, FakePwm, lambda _seconds: None)

    pwm = FakePwm.instances[-1]
    led = [pin for pin in FakePin.instances if pin.pin_id == 25][-1]
    assert pwm.duty_history[-1] == 0
    assert led.history[-1] == "消灯"


def test_run_makes_output_safe_when_interrupted(main_module):
    """LED通知中の中断時にPWMを0%へ戻してLEDを消灯する。

    関連テストID: TEST-DESN-010, TEST-DESN-013
    """
    FakePin.input_values = {1: 0, 2: 1, 3: 1, 4: 1}

    def raise_interrupt(_seconds):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        main_module.run(FakePin, FakePwm, raise_interrupt)

    pwm = FakePwm.instances[-1]
    led = [pin for pin in FakePin.instances if pin.pin_id == 25][-1]
    assert pwm.duty_history[-1] == 0
    assert led.history[-1] == "消灯"


def test_hold_pwm_output_waits_until_interrupted(main_module):
    """PWM保持処理が停止要求まで待機を継続する。

    関連テストID: TEST-DESN-006
    """
    sleep_history = []

    def raise_interrupt(seconds):
        sleep_history.append(seconds)
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        main_module.hold_pwm_output(raise_interrupt)

    assert sleep_history == [1]


def test_run_stops_pwm_and_led_when_output_is_interrupted(main_module):
    """PWM保持中の中断時にPWMを0%へ戻し、LEDを消灯する。

    関連テストID: TEST-DESN-010, TEST-DESN-013
    """
    def raise_interrupt(_seconds):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        main_module.run(FakePin, FakePwm, raise_interrupt, hold_output=True)

    pwm = FakePwm.instances[-1]
    led = [pin for pin in FakePin.instances if pin.pin_id == 25][-1]
    assert pwm.duty_history[-1] == 0
    assert led.history[-1] == "消灯"


def test_run_stops_fixed_high_output_when_interrupted(main_module):
    """100%出力中の中断時にGP0をLowへ戻してLEDを消灯する。"""
    FakePin.input_values = {1: 1, 2: 0, 3: 1, 4: 0}
    sleep_history = []

    def raise_interrupt(seconds):
        sleep_history.append(seconds)
        if len(sleep_history) == 24:
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        main_module.run(FakePin, FakePwm, raise_interrupt, hold_output=True)

    output_pin = [pin for pin in FakePin.instances if pin.pin_id == 0][-1]
    led = [pin for pin in FakePin.instances if pin.pin_id == 25][-1]
    assert output_pin.history == ["点灯", "消灯"]
    assert led.history[-1] == "消灯"
