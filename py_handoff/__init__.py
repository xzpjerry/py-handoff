import pluggy

from py_handoff.interface import BaseMessage

hookspec = pluggy.HookspecMarker("py_handoff")
hookimpl = pluggy.HookimplMarker("py_handoff")


class PyHandoffPluginSpec:
    @hookspec
    def waiting_to_capture(self):
        """This method should be blocking until it want to capture the interested state"""

    @hookspec
    def capture_state(self) -> BaseMessage:
        """Define how to capture the interested state that you want to share with the remote

        Returns:
            BaseMessage: Captured state
        """

    @hookspec
    def restore_state(self, msg: BaseMessage):
        """Define how to restore the interested state at the remote side

        Args:
            msg (BaseMessage): Restore the state based on the message
        """
