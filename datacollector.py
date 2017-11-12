import numpy as np
class Data_Collector():

    def __init__(self,model):
        self.model = model
        self.vacancies = []
        self.unemployed = []
        self.employed = []
        self.inactive = []
        self.jobseekers = []
        self.wagelist = []
        self.employer_size_list = []
        self.vacancywagelist = []
    def step(self):
        self.vacancywagelist.append(sum(list(map(lambda x:len(x.vacancy_wage_list),self.model.schedule_employers.agents))))
        self.vacancies.append(sum(list(map(lambda x:x.firm_size - len(x.employees),self.model.schedule_employers.agents))))
        self.unemployed.append(len([x for x in self.model.schedule_employees.agents if x.employer == None]))
        self.employed.append(sum(list(map(lambda x:len(x.employees), self.model.schedule_employers.agents))))
        self.jobseekers.append(len(self.model.job_seeker_pool))
        self.inactive.append(len(self.model.inactive_pool))

        self.employer_size_list.append([x.firm_size for x in self.model.schedule_employers.agents])

        self.wagelist.append([x.wage for x in self.model.schedule_employees.agents if x.employer != None])

    def print_data(self):
        print("vacancies - " + str(self.vacancies))
        print("no. of unemployed/inactive - " + str(self.unemployed))
        print("no. of employees - " + str(self.employed))
        print("no. in jspool - " + str(self.jobseekers))
        print("no. in inactive pool - " + str(self.inactive))
        print(list(map(lambda x : np.mean(x),self.wagelist)))
        print(list(map(lambda x : np.mean(x),self.employer_size_list)))
        list1 = []
        for i in range(200):
            list1.append((float(self.jobseekers[i]) / (self.jobseekers[i] + self.employed[i])) * 100)
        print(np.median(list1))
    def test(self,num_steps):
        # check 1 vacancies = no. of unemployed,inactive
        # check 2 1000 = unemployed + employees
        # check 3 JSPOOL and inactive should sum to vacancies/inactive/unemployed
        for i in range(num_steps):
            if (self.vacancies[i] != self.unemployed[i]):
                return False
            if (self.employed[i] + self.vacancies[i] != 1000):
                return False
            if (self.vacancies[i] != self.jobseekers[i] + self.inactive[i]):
                return False
            if (self.vacancies[i] != self.vacancywagelist[i]):
                return False
            return True

