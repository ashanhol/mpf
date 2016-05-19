""" Contains the parent classes Platform"""
import abc


class BasePlatform(metaclass=abc.ABCMeta):
    def __init__(self, machine):
        self.machine = machine
        self.HZ = None
        self.secs_per_tick = None
        self.next_tick_time = None
        self.features = {}
        self.log = None

        # Set default platform features. Each platform interface can change
        # these to notify the framework of the specific features it supports.
        self.features['has_dmd'] = False
        self.features['has_rgb_dmd'] = False
        self.features['has_accelerometers'] = False
        self.features['has_i2c'] = False
        self.features['has_servos'] = False
        self.features['has_matrix_lights'] = False
        self.features['has_gis'] = False
        self.features['has_leds'] = False
        self.features['has_switches'] = False
        self.features['has_drivers'] = False

    @abc.abstractmethod
    def initialize(self):
        pass

    def timer_initialize(self):
        """ Run this before the machine loop starts. I want to do it here so we
        don't need to check for initialization on each machine loop. (Or is
        this premature optimization?)

        """
        self.next_tick_time = self.machine.clock.get_time()

    def tick(self, dt):
        """Subclass this method in a platform module to perform periodic updates
        to the platform hardware, e.g. reading switches, sending driver or
        light updates, etc.

        """
        pass

    @abc.abstractmethod
    def stop(self):
        """Subclass this method in the platform module if you need to perform
        any actions to gracefully stop the platform interface.

        This could do things like reseting it, stopping events, etc.

        This method will be called when MPF stops, including when an MPF thread
        crashes.

        """
        pass


class DmdPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)
        self.features['has_dmd'] = True

    @abc.abstractmethod
    def configure_dmd(self):
        """Subclass this method in a platform module to configure the DMD.

        This method should return a reference to the DMD's platform interface
        method will will receive the frame data.

        """
        raise NotImplementedError


class RgbDmdPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)
        self.features['has_rgb_dmd'] = True

    @abc.abstractmethod
    def configure_rgb_dmd(self):
        """Subclass this method in a platform module to configure the DMD.

        This method should return a reference to the DMD's platform interface
        method will will receive the frame data.

        """
        raise NotImplementedError


class AccelerometerPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)
        self.features['has_accelerometers'] = True

    @abc.abstractmethod
    def configure_accelerometer(self, device, number, use_high_pass):
        raise NotImplementedError


class I2cPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)
        self.features['has_i2c'] = True

    @abc.abstractmethod
    def i2c_write8(self, address, register, value):
        raise NotImplementedError

    @abc.abstractmethod
    def i2c_read8(self, address, register):
        raise NotImplementedError

    @abc.abstractmethod
    def i2c_read16(self, address, register):
        raise NotImplementedError


class ServoPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)
        self.features['has_servos'] = True

    @abc.abstractmethod
    def configure_servo(self, config):
        raise NotImplementedError


class MatrixLightsPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)
        self.features['has_matrix_lights'] = True

    @abc.abstractmethod
    def configure_matrixlight(self, config):
        """Subclass this method in a platform module to configure a matrix
        light.

        This method should return a reference to the matrix lights's platform
        interface object which will be called to access the hardware.

        """
        raise NotImplementedError


class GiPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)
        self.features['has_gis'] = True

    @abc.abstractmethod
    def configure_gi(self, config):
        """Subclass this method in a platform module to configure a GI string.

        This method should return a reference to the GI string's platform
        interface object which will be called to access the hardware.

        """
        raise NotImplementedError


class LedPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)
        self.features['has_leds'] = True

    @abc.abstractmethod
    def configure_led(self, config, channels):
        """Subclass this method in a platform module to configure an LED.

        This method should return a reference to the LED's platform interface
        object which will be called to access the hardware.

        """
        raise NotImplementedError


class SwitchPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)
        self.features['has_switches'] = True

    @abc.abstractmethod
    def configure_switch(self, config):
        """Subclass this method in a platform module to configure a switch.

        This method should return a reference to the switch's platform interface
        object which will be called to access the hardware.

        """
        raise NotImplementedError

    @classmethod
    def get_switch_config_section(cls):
        return None

    @classmethod
    def get_switch_overwrite_section(cls):
        return None

    def validate_switch_overwrite_section(self, switch, config_overwrite):
        switch.machine.config_validator.validate_config(
            "switch_overwrites", config_overwrite, switch.name,
            base_spec=self.__class__.get_switch_overwrite_section())
        return config_overwrite

    def validate_switch_section(self, switch, config):
        switch.machine.config_validator.validate_config(
            "switches", config, switch.name,
            base_spec=self.__class__.get_switch_config_section())
        return config

    @abc.abstractmethod
    def get_hw_switch_states(self):
        """Subclass this method in a platform module to return the hardware
        states of all the switches on that platform.
        of a switch.

        This method should return a dict with the switch numbers as keys and the
        hardware state of the switches as values. (0 = inactive, 1 = active)
        This method should not compensate for NO or NC status, rather, it
        should return the raw hardware states of the switches.

        """
        raise NotImplementedError


class DriverPlatform(BasePlatform, metaclass=abc.ABCMeta):
    def __init__(self, machine):
        super().__init__(machine)

        # Set default platform features. Each platform interface can change
        # these to notify the framework of the specific features it supports.
        self.features['has_drivers'] = True
        self.features['max_pulse'] = 255

    @abc.abstractmethod
    def configure_driver(self, config):
        """Subclass this method in a platform module to configure a driver.

        This method should return a reference to the driver's platform interface
        object which will be called to access the hardware.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def clear_hw_rule(self, switch, coil):
        """Subclass this method in a platform module to clear a hardware switch
        rule for this switch.

        Clearing a hardware rule means actions on this switch will no longer
        affect coils.

        Another way to think of this is that it 'disables' a hardware rule.
        This is what you'd use to disable flippers and autofire_coils during
        tilt, game over, etc.

        """
        raise NotImplementedError

    @classmethod
    def get_coil_config_section(cls):
        return None

    @classmethod
    def get_coil_overwrite_section(cls):
        return None

    def validate_coil_overwrite_section(self, driver, config_overwrite):
        driver.machine.config_validator.validate_config(
            "coil_overwrites", config_overwrite, driver.name,
            base_spec=self.get_coil_overwrite_section())
        return config_overwrite

    def validate_coil_section(self, driver, config):
        driver.machine.config_validator.validate_config(
            "coils", config, driver.name,
            base_spec=self.__class__.get_coil_config_section())
        return config

    @abc.abstractmethod
    def set_pulse_on_hit_and_release_rule(self, enable_switch, coil):
        """Pulses a driver when a switch is hit. When the switch is released the pulse is canceled. Typically used on
        the main coil for dual coil flippers without eos switch. """
        raise NotImplementedError

    @abc.abstractmethod
    def set_pulse_on_hit_and_enable_and_release_rule(self, enable_switch, coil):
        """Pulses a driver when a switch is hit. Then enables the driver (may be with pwm). When the switch is released
        the pulse is canceled and the driver gets disabled. Typically used for single coil flippers. """
        raise NotImplementedError

    @abc.abstractmethod
    def set_pulse_on_hit_and_enable_and_release_and_disable_rule(self, enable_switch, disable_switch, coil):
        """Pulses a driver when a switch is hit. Then enables the driver (may be with pwm). When the switch is released
        the pulse is canceled and the driver gets disabled. When the second disable_switch is hit the pulse is canceled
        and the driver gets disabled. Typically used on the main coil for dual coil flippers with eos switch. """
        raise NotImplementedError

    @abc.abstractmethod
    def set_pulse_on_hit_rule(self, enable_switch, coil):
        """Pulses a driver when a switch is hit. When the switch is released the pulse continues. Typically used for
         autofire coils such as pop bumpers. """
        raise NotImplementedError
