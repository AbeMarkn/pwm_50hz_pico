"""Raspberry Pi Pico起動時にDIP設定を読み取り、LED通知後にPWMを開始する。

関連設計ID: DESN-SW-003, DESN-SW-006, DESN-SW-008
"""

from machine import PWM, Pin
from utime import sleep

from pwm_controller import apply_pwm, blink_value, duty_percent_for, read_switch_value

PWM_PIN_NUMBER = 0
LED_PIN_NUMBER = 25
SWITCH_PIN_NUMBERS = (1, 2, 3, 4)
STARTUP_LED_ON_SECONDS = 0.5
STARTUP_WAIT_SECONDS = 1
PWM_START_WAIT_SECONDS = 1
PWM_HOLD_INTERVAL_SECONDS = 1


def initialize_hardware(pin_factory=Pin, pwm_factory=PWM):
    """LED、DIP入力およびPWM出力を安全な初期状態にする。

    関連設計ID: DESN-HW-001～DESN-HW-005, DESN-SW-003, DESN-SW-006
    """
    led = pin_factory(LED_PIN_NUMBER, Pin.OUT)
    led.off()
    input_pins = tuple(
        pin_factory(pin_number, Pin.IN, Pin.PULL_UP)
        for pin_number in SWITCH_PIN_NUMBERS
    )
    pwm = pwm_factory(pin_factory(PWM_PIN_NUMBER))
    apply_pwm(pwm, 0)
    return led, input_pins, pwm


def run(pin_factory=Pin, pwm_factory=PWM, sleep_fn=sleep, hold_output=False):
    """起動時の読取り、LED通知、PWM設定を順に1回実行する。

    関連設計ID: DESN-SW-003, DESN-SW-006, DESN-SW-008
    """
    led = None
    pwm = None
    output_pin = None
    try:
        led, input_pins, pwm = initialize_hardware(pin_factory, pwm_factory)
        led.on()
        sleep_fn(STARTUP_LED_ON_SECONDS)
        led.off()
        sleep_fn(STARTUP_WAIT_SECONDS)
        switch_value = read_switch_value(input_pins)
        blink_value(led, switch_value, sleep_fn)
        sleep_fn(PWM_START_WAIT_SECONDS)
        duty_percent = duty_percent_for(switch_value)
        if duty_percent == 100:
            pwm.deinit()
            output_pin = pin_factory(PWM_PIN_NUMBER, Pin.OUT)
            output_pin.on()
        else:
            apply_pwm(pwm, duty_percent)
        led.on()
        if hold_output:
            hold_pwm_output(sleep_fn)
        return pwm
    except BaseException:
        if output_pin is not None:
            try:
                output_pin.off()
            except BaseException:
                pass
        if pwm is not None:
            try:
                apply_pwm(pwm, 0)
            except BaseException:
                pass
        if led is not None:
            try:
                led.off()
            except BaseException:
                pass
        raise


def hold_pwm_output(sleep_fn=sleep):
    """PWMオブジェクトを保持するため、停止されるまで待機する。"""
    while True:
        sleep_fn(PWM_HOLD_INTERVAL_SECONDS)


if __name__ == "__main__":
    active_pwm = run(hold_output=True)
