from mesa import Model
from agents import Employer_Agent,Employee_Agent
from mesa.time import BaseScheduler
import numpy as np
import random
##add in datacollectors so we can see it work
class Labor_Model(Model):
    def __init__(self,num_employee=1000,num_employer=10,num_jobseekers=10,wage_flexibility=(0.1,0.1),p_1=0.01,p_2=0.01,p_3=0.01):
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

        self.create_employee(self.num_employee)
        self.create_employer(self.num_employer,self.num_employee,wage_flexibility)

        # print(len(self.employee_seeker_pool))
        # print(len(self.job_seeker_pool))

        ## INIT ALLOCATING FIRMS TO WORKERS
        while(self.employee_seeker_pool or self.job_seeker_pool):
            employer = random.choice(self.employee_seeker_pool)

            for i in range(employer.firm_size):
                employee = random.choice(self.job_seeker_pool)
                self.change_employer(employee,employer)

        # print([str(a.employer) for a in self.schedule_employees.agents])
        # print(self.employee_seeker_pool)
        # print(self.job_seeker_pool)

        ## ADDING JOB SEEKERS
        for i in range(self.num_jobseekers):
            a = random.choice(self.schedule_employees.agents)
            while(a.employer == None):
                a = random.choice(self.schedule_employees.agents)
            self.change_employer(a,employer=None)

        # print(len(self.job_seeker_pool))
        # print(len(self.employee_seeker_pool))
        # print([str(a) for a in self.job_seeker_pool])
        # print([str(a) for a in self.employee_seeker_pool])

        ##FIND JOBS
        self.job_search()

        # print(len(self.job_seeker_pool))
        # print(len(self.employee_seeker_pool))
        # print([str(a.unique_id) for a in self.job_seeker_pool])
        # print([str(a) for a in self.employee_seeker_pool])

    def testing(self):
        vacancies = map(lambda x: x.firm_size - len(x.employees), self.schedule_employers.agents)
        employees = map(lambda x:len(x.employees), self.schedule_employers.agents)
        unemployed = [b for b in self.schedule_employees.agents if b.employer == None]
        print("vacancies - " + str(sum(list(vacancies))))
        print("no. of unemployed/inactive - " + str(len(unemployed)))

        print("no. of employees - " + str(sum(list(employees))))
        print("no in active - " + str(len([x for x in self.schedule_employees.agents if(x not in self.job_seeker_pool and x not in self.inactive_pool)])))

        print("no. in jspool - " + str(len(self.job_seeker_pool)))
        # print([x.unique_id for x in self.job_seeker_pool])
        print("no. in inactive pool - " + str(len(self.inactive_pool)))
        # print([x.unique_id for x in self.inactive_pool])
        print("no. in total employees - " + str(len(self.schedule_employees.agents)))
        print("no. in total employers - " + str(len(self.schedule_employers.agents)))


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
            # print(employee)
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
                    # print("...." + str(employee))
                    # print("..... " + str([str(a) for a in employee.employer.employees]))
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
        for e in self.employee_seeker_pool:
            # print("job hunting")
            for wage in e.vacancy_wage_list:
                allowable_wage = (wage * (1-e.wage_flexibility[0]), wage * (1+e.wage_flexibility[1]))
                possible_candidates = []
                for a in self.job_seeker_pool:
                    if(allowable_wage[0] <= a.wage <= allowable_wage[1] and a.past_employer != e):
                        possible_candidates.append(a)
                if(possible_candidates):
                    # print("found")
                    # print(e)
                    # for i in possible_candidates:
                    #     print(i)
                    # print("-----")
                    chosen_candidate = sorted(possible_candidates,key=lambda x:x.wage)[0]
                    chosen_candidate.wage = wage
                    self.change_employer(chosen_candidate,e)
                    e.vacancy_wage_list.remove(wage)


    def step(self):
        print("start")
        self.testing()
        print()

        ##wipe inactive ppl and add in new peeps
        if(self.inactive_pool):
            for i in self.inactive_pool:
                self.schedule_employees.remove(i)
            self.create_employee(len(self.inactive_pool))
            self.inactive_pool = []

        print("before age")
        self.testing()
        print()

        ##Age everyone
        self.schedule_employees.step()
        retiree = [a for a in self.schedule_employees.agents if a.age >= 60.0]
        # print("retiree" + str(len(retiree)))
        for r in retiree:
            self.change_employer(r,employer=None,leaving_wf=True)
        # print("inactive poool" + str(len(self.inactive_pool)))

        print("before leaving WF")
        self.testing()
        print()


        ##Employed & Unemployed peeps leaving WF
        employed_list = [x for x in self.schedule_employees.agents if x not in self.job_seeker_pool and x not in self.inactive_pool]
        for i in range(int(self.p_3 * len(employed_list))):
            # print("self schedule employees")
            # print([str(a) for a in self.schedule_employees.agents])
            a = random.choice(employed_list)
            self.change_employer(a,employer=None,leaving_wf=True)
            employed_list.remove(a)
        unemployed_list = [x for x in self.job_seeker_pool if x not in self.inactive_pool]
        for i in range(int(self.p_2 * len(unemployed_list))):
            a = random.choice(unemployed_list)
            self.change_employer(a, employer=None,leaving_wf=True)
            unemployed_list.remove(a)

        print("before quitting")
        self.testing()
        print()


        ##Employed peeps quitting
        employed_list = [x for x in self.schedule_employees.agents if x not in self.job_seeker_pool and x not in self.inactive_pool]
        for i in range(int(self.p_1) * len(employed_list)):
            a = random.choice(employed_list)
            self.change_employer(a,employer=None)
            employed_list.remove(a)

        print("before closing down")
        self.testing()
        print()


        ##Employers closing down
        firm_size = 0
        for i in range(self.p_4):
            a = random.choice(self.schedule_employers.agents)
            print(a)
            firm_size += a.firm_size
            self.schedule_employers.remove(a)
            if(a in self.employee_seeker_pool):
                self.employee_seeker_pool.remove(a)
            employee_list = a.employees[:]
            for w in employee_list:
                self.change_employer(w,employer=None,employer_closed=True)

        print("before new entry")
        self.testing()
        print()


        ##Employers entering
        self.create_employer(self.p_4,firm_size,self.wage_flexibility,add_vacancy_wage_list=True)

        print("before job matching")
        self.testing()
        print()


        ##Job matching occurs
        self.job_search()

        print("END")
        self.testing()
        print()





