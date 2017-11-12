from model import Labor_Model

m = Labor_Model()
for i in range(100):
    print("cycle number - " + str(i))
    m.step()