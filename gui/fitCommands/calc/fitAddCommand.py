import wx
from logbook import Logger

import eos.db
from service.fit import Fit


pyfalog = Logger(__name__)


class FitAddCommandCommand(wx.Command):

    def __init__(self, fitID, commandFitID, state=None):
        wx.Command.__init__(self, True)
        self.fitID = fitID
        self.commandFitID = commandFitID
        self.state = state

    def Do(self):
        pyfalog.debug('Doing addition of command fit {} for fit {}'.format(self.commandFitID, self.fitID))
        sFit = Fit.getInstance()
        fit = sFit.getFit(self.fitID)
        commandFit = sFit.getFit(self.commandFitID)

        # Command fit could have been deleted if we were redoing
        if commandFit is None:
            pyfalog.debug('Command fit is not available')
            return False
        # Already commanding this ship
        if commandFit in fit.commandFits:
            pyfalog.debug('Command fit had been applied already')
            return False

        fit.commandFitDict[commandFit.ID] = commandFit
        # this bit is required -- see GH issue # 83
        eos.db.saveddata_session.flush()
        eos.db.saveddata_session.refresh(commandFit)

        if self.state is not None:
            fitCommandInfo = commandFit.getCommandInfo(self.fitID)
            if fitCommandInfo is None:
                pyfalog.warning('Fit command info is not available')
                self.Undo()
                return False
            fitCommandInfo.active = self.state

        eos.db.commit()
        return True

    def Undo(self):
        pyfalog.debug('Undoing addition of command fit {} for fit {}'.format(self.commandFitID, self.fitID))
        # Can't find the command fit, it must have been deleted. Just skip, as deleted fit
        # means that someone else just did exactly what we wanted to do
        commandFit = Fit.getInstance().getFit(self.commandFitID)
        if commandFit is None:
            return True
        from .fitRemoveCommand import FitRemoveCommandCommand
        cmd = FitRemoveCommandCommand(fitID=self.fitID, commandFitID=self.commandFitID)
        return cmd.Do()
