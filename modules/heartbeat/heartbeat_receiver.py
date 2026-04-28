"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
DISCONNECT_THRESHOLD = 5
HEARTBEAT_PERIOD = 1
CONNECTED = "Connected"
DISCONNECTED = "Disconnected"


class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> "tuple[bool, HeartbeatReceiver | None]":
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """

        if connection is None:
            local_logger.error("Failed to create Heartbeat receiver. No connection provided.", True)
            return False, None

        return True, cls(cls.__private_key, connection, local_logger)

    def __init__(
        self, key: object, connection: mavutil.mavfile, local_logger: logger.Logger
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        # Do any intializiation here
        self.__connection = connection
        self.__logger = local_logger

        self.__current_state = DISCONNECTED
        self.__missed_heartbeat_count = 0

    def run(self) -> "tuple[bool, str]":
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        try:
            msg = self.__connection.recv_match(
                type="HEARTBEAT",
                blocking=True,
                timeout=HEARTBEAT_PERIOD,
            )
        # pylint: disable-next=broad-exception-caught
        except Exception as exception:
            self.__logger.error(
                f"Failed while receiving heartbeat: {exception}",
                True,
            )
            return False, self.__current_state

        if msg is not None and msg.get_type() == "HEARTBEAT":
            self.__missed_heartbeat_count = 0
            self.__current_state = CONNECTED
            self.__logger.info("Received Heartbeat", True)
            return True, self.__current_state

        self.__missed_heartbeat_count += 1
        self.__logger.warning(
            f"Missed Heartbeat. Missed Count Now: {self.__missed_heartbeat_count}.", True
        )

        if self.__missed_heartbeat_count >= DISCONNECT_THRESHOLD:
            self.__current_state = DISCONNECTED

        return True, self.__current_state


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
