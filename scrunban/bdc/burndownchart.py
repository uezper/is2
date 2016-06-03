import matplotlib.pyplot as plt

class Burndownchart():
    def __init__(self, project_name, total_time, lapse_time, ideal=True, grid=True, units='dias'):
        self.project_name = project_name
        self.total_time = total_time
        self.lapse_time = lapse_time
        self.x_units = units
        self.ideal = ideal
        self.grid = grid

    def loadWork(self, work):
        self.work = work

    def build(self, filename):
        if self.ideal:
            plt.plot([0, self.total_time], [self.total_time, 0], '--g', label='Rendimiento ideal')
        if self.grid == True:
            plt.grid(True)

        try:
            plt.plot(self.work, '-or', label='Rendimiento actual')
        except AttributeError:
            print('Load work using loadWork!')
            
        plt.axis([0, self.total_time, 0, self.total_time])
        plt.title('Burndown chart de {}'.format(self.project_name))
        plt.ylabel('Trabajo restante') # TODO Add units
        plt.xlabel('Tiempo ({})'.format(self.x_units))
        plt.legend()
        plt.savefig(filename)
        # plt.show()

def main():
    points = [20, 18, 16, 16, 17, 15, 14, 12, 11, 9]
    bdc = Burndownchart('IS2 Project', 20, 10)
    bdc.loadWork(points)
    bdc.build('burndownchart.png')

if __name__ == '__main__':
    main()
