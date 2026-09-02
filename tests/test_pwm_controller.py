"""PWM制御モジュールの実機なし自動テスト。

関連設計ID: DESN-SW-004, DESN-SW-005, DESN-SW-008
"""

import pytest

from pwm_controller import (
    LED_HALF_PERIOD_SECONDS,
    PWM_FREQUENCY_HZ,
    apply_pwm,
    blink_value,
    duty_percent_for,
    duty_u16_for,
    read_switch_value,
)


class FakePin:
    """入力値とLED操作履歴を保持するテスト用端子。

    関連設計ID: DESN-SW-005
    """

    def __init__(self, value=1):
        self._value = value
        self.history = []
        self.read_count = 0

    def value(self):
        self.read_count += 1
        return self._value

    def on(self):
        self.history.append("点灯")

    def off(self):
        self.history.append("消灯")


class FakePwm:
    """PWM APIの設定履歴を保持するテスト用オブジェクト。

    関連設計ID: DESN-SW-005
    """

    def __init__(self):
        self.frequency = None
        self.duty = None

    def freq(self, frequency):
        self.frequency = frequency

    def duty_u16(self, duty):
        self.duty = duty


@pytest.mark.parametrize("switch_value", range(16))
def test_read_switch_value_all_combinations(switch_value):
    """16通りの負論理入力を正しい設定値へ変換する。

    関連テストID: TEST-DESN-001
    """
    input_pins = [
        FakePin(0 if switch_value & (1 << bit_index) else 1)
        for bit_index in range(4)
    ]

    assert read_switch_value(input_pins) == switch_value
    assert [pin.read_count for pin in input_pins] == [1, 1, 1, 1]


@pytest.mark.parametrize(
    ("switch_value", "expected_duty"),
    [(value, value * 10) for value in range(11)]
    + [(value, 0) for value in range(11, 16)],
)
def test_duty_percent_for_all_switch_values(switch_value, expected_duty):
    """有効値と異常値を仕様どおりのデューティ比へ変換する。

    関連テストID: TEST-SPEC-001, TEST-SPEC-005, TEST-DESN-002
    """
    assert duty_percent_for(switch_value) == expected_duty


@pytest.mark.parametrize(
    ("duty_percent", "expected_u16"),
    [(value, (65535 * value + 50) // 100) for value in range(0, 101, 10)],
)
def test_duty_u16_for_all_supported_percentages(duty_percent, expected_u16):
    """10%刻みの値を16ビット値へ四捨五入する。

    関連テストID: TEST-DESN-002
    """
    assert duty_u16_for(duty_percent) == expected_u16


@pytest.mark.parametrize("switch_value", range(16))
def test_blink_value_count_and_timing(switch_value):
    """LED回数、待機時間および終了時消灯を確認する。

    関連テストID: TEST-SPEC-004, TEST-SPEC-005, TEST-DESN-003
    """
    led = FakePin()
    sleep_history = []

    blink_value(led, switch_value, sleep_history.append)

    assert led.history == ["消灯"] + ["点灯", "消灯"] * switch_value + ["消灯"]
    assert sleep_history == [LED_HALF_PERIOD_SECONDS] * (switch_value * 2)


def test_blink_value_turns_led_off_when_sleep_fails():
    """待機処理の例外時にもLEDを消灯する。

    関連テストID: TEST-DESN-010
    """
    led = FakePin()

    def raise_error(_seconds):
        raise RuntimeError("待機失敗")

    with pytest.raises(RuntimeError, match="待機失敗"):
        blink_value(led, 1, raise_error)

    assert led.history[-1] == "消灯"


@pytest.mark.parametrize("invalid_value", [-1, 16, 1.0, "1", None, True])
def test_duty_percent_for_rejects_invalid_values(invalid_value):
    """設定値の範囲外および整数以外を拒否する。

    関連テストID: TEST-DESN-009
    """
    with pytest.raises(ValueError):
        duty_percent_for(invalid_value)


@pytest.mark.parametrize("invalid_value", [-1, 101, 10.0, "10", None, False])
def test_duty_u16_for_rejects_invalid_values(invalid_value):
    """デューティ比の範囲外および整数以外を拒否する。

    関連テストID: TEST-DESN-009
    """
    with pytest.raises(ValueError):
        duty_u16_for(invalid_value)


@pytest.mark.parametrize("invalid_value", [-1, 101, 10.0, "10", None, False])
def test_apply_pwm_rejects_invalid_values_without_side_effects(invalid_value):
    """不正なデューティ比ではPWM設定を変更しない。

    関連テストID: TEST-DESN-009
    """
    pwm = FakePwm()

    with pytest.raises(ValueError):
        apply_pwm(pwm, invalid_value)

    assert pwm.frequency is None
    assert pwm.duty is None


def test_read_switch_value_rejects_wrong_pin_count():
    """4個以外の入力端子を拒否する。

    関連テストID: TEST-DESN-009
    """
    with pytest.raises(ValueError):
        read_switch_value([FakePin()] * 3)


def test_read_switch_value_rejects_non_binary_input():
    """0と1以外の入力値を拒否する。

    関連テストID: TEST-DESN-009, TEST-DESN-010
    """
    with pytest.raises(ValueError):
        read_switch_value([FakePin(), FakePin(), FakePin(2), FakePin()])


@pytest.mark.parametrize("duty_percent", range(0, 101, 10))
def test_apply_pwm_sets_frequency_and_duty(duty_percent):
    """PWMへ50 Hzと変換済みデューティ値を設定する。

    関連テストID: TEST-DESN-002
    """
    pwm = FakePwm()

    apply_pwm(pwm, duty_percent)

    assert pwm.frequency == PWM_FREQUENCY_HZ
    assert pwm.duty == duty_u16_for(duty_percent)
