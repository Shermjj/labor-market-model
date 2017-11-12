from model import Labor_Model

m = Labor_Model()
for i in range(200):
    m.step()
m.datacollector.print_data()
print(m.datacollector.test(200))