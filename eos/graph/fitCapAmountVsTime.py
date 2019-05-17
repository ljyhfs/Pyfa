import math

from eos.graph import Graph


class FitCapAmountVsTimeGraph(Graph):

    def getPlotPoints(self, fit, extraData, xRange, xAmount):
        xs = []
        ys = []
        for x in self._xIter(xRange, xAmount):
            xs.append(x)
            ys.append(self.calc(fit, x))
        return xs, {'capAmount': ys}

    def getYForX(self, fit, extraData, x):
        return {'capAmount': self.calc(fit, x)}

    @staticmethod
    def calc(fit, time):
        if time < 0:
            return 0
        maxCap = fit.ship.getModifiedItemAttr('capacitorCapacity')
        regenTime = fit.ship.getModifiedItemAttr('rechargeRate') / 1000
        # https://wiki.eveuniversity.org/Capacitor#Capacitor_recharge_rate
        cap = maxCap * (1 + math.exp(5 * -time / regenTime) * -1) ** 2
        return cap