_D='bracket'
_C='max'
_B='min'
_A='rate'
def get_holiday_allowance(gross_year):return round(gross_year*.08/1.08)
def get_net_year(taxable_year,income_tax):return round(taxable_year+income_tax)
def get_rates(brackets,salary,kind):
	G='inf';D=salary;C=0
	for A in brackets:
		E=A.get(_C,float(G))-A[_B]if A.get(_C)else float(G);B=round(A.get(kind,A[_A])*100000)/100000;F=-1<B<1 and B!=0
		if D<=E or not A.get(_C):
			if F:H=round(D*B,2);C+=H
			else:C=B
			break
		else:
			if F:C+=round(E*B,2)
			else:C=B
			D-=E
	return round(C,2)
def get_payroll_tax(salary):A=[{_D:1,_B:0,_C:38097,_A:.0932},{_D:2,_B:38098,_C:75517,_A:.3697},{_D:3,_B:75518,_A:.495}];return get_rates(A,salary,_A)
def get_social_tax(salary):A='social';B=[{_D:1,_B:0,_C:38097,_A:.3697,A:.2765,'older':.0975}];return get_rates(B,salary,A)
def get_general_credit(salary):A=[{_D:1,_B:0,_C:24813,_A:3362},{_D:2,_B:24813,_C:75518,_A:-.0663},{_D:3,_B:75519,_A:0}];B=get_rates(A,salary,_A);return B
def get_labour_credit(salary):
	A=salary;B=9094;C=[{_D:1,_B:0,_C:11490,_A:.08425},{_D:2,_B:11490,_C:24820,_A:.31433},{_D:3,_B:24820,_C:39957,_A:.02471},{_D:4,_B:39957,_C:124934,_A:-.0651},{_D:5,_B:115296,_A:0}]
	if A<B:return 0
	return get_rates(C,A,_A)





salary_input = {
    "gross_year": 32400,
    "holidayAllowance": False,
    "hours": 40,
}

gross_year = salary_input.get('gross_year', 0)
gross_month = salary_input.get('gross_month', 0)
gross_week = salary_input.get('gross_week', 0)
gross_day = salary_input.get('gross_day', 0)
gross_hour = salary_input.get('gross_hour', 0)

gross_year = round(gross_year + gross_month * 12 + gross_week * 52 + gross_day * 255 + gross_hour * 52 * salary_input['hours'])


gross_holiday_allowance = get_holiday_allowance(gross_year) if salary_input['holidayAllowance'] else 0
taxable_year = round(gross_year - gross_holiday_allowance)
payroll_tax = -1 * get_payroll_tax(taxable_year)
social_tax = -1 * get_social_tax(taxable_year)
labour_credit = get_labour_credit(taxable_year)
general_credit = get_general_credit(taxable_year)
income_tax = round(payroll_tax + social_tax + labour_credit + general_credit)
net_year = get_net_year(taxable_year, income_tax)
net_allowance = get_holiday_allowance(net_year) if salary_input['holidayAllowance'] else 0

print(f"payroll_tax: {payroll_tax}")
print(f"social_tax: {social_tax}")
print(f"social_credit: {1}")
print(f"labour_credit: {labour_credit}")
print(f"general_credit: {general_credit}")
print(f"net_year: {net_year}")
print(f"net_month: {net_year/12}")