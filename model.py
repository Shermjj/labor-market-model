from mesa import Model
from agents import Employer_Agent,Employee_Agent
from datacollector import Data_Collector
from mesa.time import BaseScheduler
import numpy as np
import random

##add in datacollectors so we can see it work
class Labor_Model(Model):
    def __init__(self,num_employee=1000,num_employer=10,num_jobseekers=10,wage_flexibility=(0.5,0.5),p_1=0.01,p_2=0.01,p_3=0.01):
        self.num_employer = num_employer
        self.employer_index = 0
        self.num_employee = num_employee
        self.employee_index = 0
        self.num_jobseekers = num_jobseekers
        self.wage_flexibility = wage_flexibility
        self.p_1 = p_1
        self.p_2 = p_2
        self.p_3 = p_3
        self.p_4 = 1
        self.schedule_employees = BaseScheduler(self)
        self.schedule_employers = BaseScheduler(self)
        self.job_seeker_pool = []
        self.inactive_pool = []
        self.employee_seeker_pool = []
        self.datacollector = Data_Collector(self)
        self.create_employee(self.num_employee)
        self.create_employer(self.num_employer,self.num_employee,wage_flexibility)

        ## INIT ALLOCATING FIRMS TO WORKERS
        while(self.employee_seeker_pool or self.job_seeker_pool):
            employer = random.choice(self.employee_seeker_pool)

            for i in range(employer.firm_size):
                employee = random.choice(self.job_seeker_pool)
                self.change_employer(employee,employer)

        ## ADDING JOB SEEKERS
        for i in range(self.num_jobseekers):
            a = random.choice(self.schedule_employees.agents)
            while(a.employer == None):
                a = random.choice(self.schedule_employees.agents)
            self.change_employer(a,employer=None)

        ##FIND JOBS
        self.job_search()

    def create_employee(self,num):
        wage_list = self.create_wage_list(num)
        age_list = [a / 4.0 for a in range(80, 240)]

        for i in range(self.employee_index,self.employee_index + num):
            age = random.choice(age_list)
            a = Employee_Agent(i, self, wage_list[i-self.employee_index], age)
            self.job_seeker_pool.append(a)
            self.schedule_employees.add(a)
        self.employee_index += num

    def create_employer(self,num_employer,num_employee,wage_flexibility,add_vacancy_wage_list=False):
        firm_size_list = self.create_firm_size_list(num_employer,num_employee)

        for i in range(self.employer_index,self.employer_index + num_employer):
            a = Employer_Agent(i,self,firm_size_list[i-self.employer_index],wage_flexibility)
            self.employee_seeker_pool.append(a)
            self.schedule_employers.add(a)
            if(add_vacancy_wage_list):
                wage_list = self.create_wage_list(num_employee)
                a.vacancy_wage_list.extend(wage_list)
        self.employer_index += num_employer

    def create_wage_list(self,num):
        list = []
        for i in range(num):
            list.append(np.random.lognormal(mean=100,sigma=0.7))
        mean_val = float(sum(list)) / len(list)
        normalized_list = [(100 / mean_val) * list[i] for i in range(num)]

        return np.round(normalized_list).astype(int).tolist()

    def create_firm_size_list(self,num_employer,num_employee):
        list = []
        for i in range(num_employer):
            list.append(np.random.power(1))
        mean_val = float(sum(list)) / len(list)
        new_mean_val = num_employee / num_employer
        normalized_list = [(new_mean_val / mean_val) * list[i] for i in range(num_employer)]
        normalized_list = np.round(normalized_list,decimals=0).astype(int).tolist()
        if(sum(normalized_list) != num_employee):
            diff = num_employee - sum(normalized_list)
            normalized_list[normalized_list.index(max(normalized_list))] += diff

        return normalized_list

    def change_employer(self,employee,employer,change_past_employer=True,leaving_wf = False,employer_closed=False):
        ##If they are changing employers
        if(employer is not None):
            employer.employees.append(employee)
            employer.employee_wage_list.append(employee.wage)
            employee.employer = employer
            self.job_seeker_pool.remove(employee)
            if(len(employer.employees) == employer.firm_size):
                self.employee_seeker_pool.remove(employee.employer)
        ##If they are either leaving the WF or quitting/retrenched
        else:
            ##not leaving the work-fore
            if(not leaving_wf):
                self.job_seeker_pool.append(employee)
                employee.employer.employees.remove(employee)
                employee.employer.employee_wage_list.remove(employee.wage)
                employee.employer.vacancy_wage_list.append(employee.wage)
                if (not employee.employer in self.employee_seeker_pool and not employer_closed):
                    self.employee_seeker_pool.append(employee.employer)
                if (change_past_employer):
                    employee.past_employer = employee.employer
                employee.employer = None

            ##If they are leaving the workforce
            else:

                if(employee in self.job_seeker_pool):
                    self.job_seeker_pool.remove(employee)
                else:
                    employee.employer.employees.remove(employee)
                    employee.employer.employee_wage_list.remove(employee.wage)
                    employee.employer.vacancy_wage_list.append(employee.wage)
                    if (not employee.employer in self.employee_seeker_pool and not employer_closed):
                        self.employee_seeker_pool.append(employee.employer)
                    if (change_past_employer):
                        employee.past_employer = employee.employer
                employee.employer = None
                self.inactive_pool.append(employee)

    def job_search(self):
        list = []
        for e in self.employee_seeker_pool:
            for wage in e.vacancy_wage_list:
                list.append((e,wage))
        sortedlist = sorted(list,key=lambda x : x[1],reverse=True)

        for employer, wage in sortedlist:
            possible_candidates = []
            for a in self.job_seeker_pool:
                allowable_wage = (a.wage * (1 - e.wage_flexibility[0]), a.wage * (1 + e.wage_flexibility[1]))
                if (allowable_wage[0] <= wage <= allowable_wage[1] and a.past_employer != employer):
                    possible_candidates.append(a)
            if (possible_candidates):
                # print([str(x) for x in possible_candidates])
                chosen_candidate = sorted(possible_candidates, key=lambda x: x.wage,reverse=True)[0]
                # print(chosen_candidate)
                chosen_candidate.wage = wage
                self.change_employer(chosen_candidate, employer)
                employer.vacancy_wage_list.remove(wage)


    def step(self):
        ##wipe inactive ppl and add in new peeps
        if(self.inactive_pool):
            for i in self.inactive_pool:
                self.schedule_employees.remove(i)
            self.create_employee(len(self.inactive_pool))
            self.inactive_pool = []

        ##Age everyone
        self.schedule_employees.step()
        retiree = [a for a in self.schedule_employees.agents if a.age >= 60.0]
        for r in retiree:
            self.change_employer(r,employer=None,leaving_wf=True)

        ##Employed & Unemployed peeps leaving WF
        employed_list = [x for x in self.schedule_employees.agents if x not in self.job_seeker_pool and x not in self.inactive_pool]
        for i in range(int(self.p_3 * len(employed_list))):
            a = random.choice(employed_list)
            self.change_employer(a,employer=None,leaving_wf=True)
            employed_list.remove(a)
        unemployed_list = [x for x in self.job_seeker_pool if x not in self.inactive_pool]
        for i in range(int(self.p_2 * len(unemployed_list))):
            a = random.choice(unemployed_list)
            self.change_employer(a, employer=None,leaving_wf=True)
            unemployed_list.remove(a)

        ##Employed peeps quitting (but not leaving the WF)
        employed_list = [x for x in self.schedule_employees.agents if x not in self.job_seeker_pool and x not in self.inactive_pool]
        for i in range(int(self.p_1) * len(employed_list)):
            a = random.choice(employed_list)
            self.change_employer(a,employer=None)
            employed_list.remove(a)

        ##Employers closing down
        firm_size = 0
        for i in range(self.p_4):
            a = random.choice(self.schedule_employers.agents)
            firm_size += a.firm_size
            self.schedule_employers.remove(a)
            if(a in self.employee_seeker_pool):
                self.employee_seeker_pool.remove(a)
            employee_list = a.employees[:]
            for w in employee_list:
                self.change_employer(w,employer=None,employer_closed=True)

        ##Employers entering
        self.create_employer(self.p_4,firm_size,self.wage_flexibility,add_vacancy_wage_list=True)

        ##Job matching occurs
        self.job_search()

        self.datacollector.step()




