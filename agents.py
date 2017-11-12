from mesa import Agent,Model


class Employee_Agent(Agent):
    def __init__(self,unique_id,model,wage,age):
        super().__init__(unique_id,model)
        self.wage = wage
        self.employer = None
        self.past_employer = None
        self.age = age

    def step(self):
        self.age += 0.25

    def __str__(self):
        return "Worker - " + str(self.unique_id) + " wage - " + str(self.wage) + " current employer " + str(self.employer) + \
               " past employer " + str(self.past_employer) + " age - " + str(self.age)

class Employer_Agent(Agent):
    def __init__(self,unique_id,model,firm_size,wage_flexibility):
        super().__init__(unique_id,model)
        self.firm_size = firm_size
        self.employees = []
        self.employee_wage_list = []
        self.vacancy_wage_list = []
        self.wage_flexibility = wage_flexibility

    def __str__(self):
        return "Boss number - " + str(self.unique_id) + "firm size - " + str(self.firm_size) \
               + "no. of employees - " + str(len(self.employees)) + " len vacancy wage list- " + str(len(self.vacancy_wage_list))

    def step(self):
        pass
