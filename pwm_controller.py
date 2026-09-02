"""DIP設定値の読取り、LED通知、PWM設定を提供するモジュール。

関連設計ID: DESN-SW-004
"""

PWM_FREQUENCY_HZ = 50
LED_HALF_PERIOD_SECONDS = 0.25
MIN_SWITCH_VALUE = 0
MAX_SWITCH_VALUE = 15
MAX_VALID_PWM_VALUE = 10


def _validate_integer_range(value, minimum, maximum, name):
    """整数値が指定範囲内であることを検証する。

    関連設計ID: DESN-SW-004, DESN-SW-008
    """
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name}は{minimum}から{maximum}の整数で指定してください")


def read_switch_value(input_pins):
    """GP1からGP4の負論理入力を設定値0から15へ変換する。

    関連設計ID: DESN-SW-004
    """
    if len(input_pins) != 4:
        raise ValueError("入力端子はGP1からGP4の順で4個指定してください")

    switch_value = 0
    for bit_index, input_pin in enumerate(input_pins):
        pin_value = input_pin.value()
        if pin_value not in (0, 1):
            raise ValueError("入力端子の値は0または1である必要があります")
        if pin_value == 0:
            switch_value |= 1 << bit_index

    return switch_value


def duty_percent_for(switch_value):
    """設定値を10%刻みのデューティ比へ変換する。

    関連設計ID: DESN-SW-004
    """
    _validate_integer_range(
        switch_value,
        MIN_SWITCH_VALUE,
        MAX_SWITCH_VALUE,
        "設定値",
    )
    if switch_value <= MAX_VALID_PWM_VALUE:
        return switch_value * 10
    return 0


def blink_value(led, switch_value, sleep_fn):
    """設定値と同じ回数だけLEDを0.5秒周期で点滅させる。

    関連設計ID: DESN-SW-004, DESN-SW-008
    """
    _validate_integer_range(
        switch_value,
        MIN_SWITCH_VALUE,
        MAX_SWITCH_VALUE,
        "設定値",
    )

    led.off()
    try:
        for _ in range(switch_value):
            led.on()
            sleep_fn(LED_HALF_PERIOD_SECONDS)
            led.off()
            sleep_fn(LED_HALF_PERIOD_SECONDS)
    finally:
        led.off()


def duty_u16_for(duty_percent):
    """百分率を四捨五入して16ビットデューティ値へ変換する。

    関連設計ID: DESN-SW-004
    """
    _validate_integer_range(duty_percent, 0, 100, "デューティ比")
    return (65535 * duty_percent + 50) // 100


def apply_pwm(pwm, duty_percent):
    """PWMへ50 Hzと指定デューティ比を設定する。

    関連設計ID: DESN-SW-004
    """
    duty_u16 = duty_u16_for(duty_percent)
    pwm.freq(PWM_FREQUENCY_HZ)
    pwm.duty_u16(duty_u16)
