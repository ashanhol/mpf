""" Contains the base class for autofire coil devices."""
from mpf.devices.switch import ReconfigureSwitch

from mpf.core.system_wide_device import SystemWideDevice


class AutofireCoil(SystemWideDevice):
    """Base class for coils in the pinball machine which should fire
    automatically based on switch activity using hardware switch rules.

    autofire_coils are used when you want the coils to respond "instantly"
    without waiting for the lag of the python game code running on the host
    computer.

    Examples of autofire_coils are pop bumpers, slingshots, and flippers.

    Args: Same as Device.
    """

    config_section = 'autofire_coils'
    collection = 'autofires'
    class_label = 'autofire'

    def _initialize(self):
        self.coil = self.config['coil']
        self.switch = ReconfigureSwitch(self.config['switch'], self.config, self.config['reverse_switch'])

        self.validate()

        self.debug_log('Platform Driver: %s', self.platform)

    def validate(self):
        """Autofire rules only work if the switch is on the same platform as the
        coil.

        In the future we may expand this to support other rules various platform
        vendors might have.

        """

        if self.switch.platform == self.coil.platform:
            self.platform = self.coil.platform
            return True
        else:
            return False

    def enable(self, **kwargs):
        """Enables the autofire coil rule."""
        del kwargs

        self.log.debug("Enabling")

        self.platform.set_hw_rule(switch_obj=self.switch,
                                  sw_name=False,
                                  sw_activity=1,
                                  driver_name=self.coil.name,
                                  driver_action='pulse',
                                  disable_on_release=False,
                                  **self.config)

    def disable(self, **kwargs):
        """Disables the autofire coil rule."""
        del kwargs
        self.log.debug("Disabling")
        self.platform.clear_hw_rule(self.switch.name)
