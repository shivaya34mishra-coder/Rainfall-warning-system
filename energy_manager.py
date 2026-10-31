from config import (
    POWER_LIMIT,
    CRITICAL_POWER_LIMIT
)


class EnergyManager:

    def __init__(
        self,
        simulator
    ):

        self.simulator = simulator


    def manage_energy(
        self,
        power
    ):

        action = (
            "NORMAL OPERATION"
        )


        # ------------------------------
        # CRITICAL CONDITION
        # ------------------------------

        if power > CRITICAL_POWER_LIMIT:

            # Switch OFF
            # lighting first

            self.simulator.set_load_status(
                "lighting",
                False
            )

            # Switch OFF
            # cooling next

            self.simulator.set_load_status(
                "cooling",
                False
            )


            action = (
                "CRITICAL: "
                "Lighting and Cooling "
                "Switched OFF"
            )


        # ------------------------------
        # HIGH POWER CONDITION
        # ------------------------------

        elif power > POWER_LIMIT:

            # Switch OFF
            # lowest priority load

            self.simulator.set_load_status(
                "lighting",
                False
            )


            action = (
                "HIGH POWER: "
                "Lighting Switched OFF"
            )


        # ------------------------------
        # NORMAL CONDITION
        # ------------------------------

        else:

            action = (
                "NORMAL OPERATION"
            )


        return action