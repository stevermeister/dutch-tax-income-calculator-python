def get_holiday_allowance(gross_year):
    return round(gross_year * 0.08 / 1.08) # Vakantiegeld (8%)

def get_net_year(taxable_year, income_tax):
    return round(taxable_year + income_tax)

def get_rates(brackets, salary, kind):
    amount = 0
    for bracket in brackets:
        delta = bracket.get('max', float('inf')) - bracket['min'] if bracket.get('max') else float('inf')
        tax = round((bracket.get(kind, bracket["rate"])) * 100000) / 100000
        is_percent = -1 < tax < 1 and tax != 0

        if salary <= delta or not bracket.get('max'):
            if is_percent:
                calculated_amount = round(salary * tax, 2)
                amount += calculated_amount
            else:
                amount = tax  
            break  
        else:
            if is_percent:
                amount += round(delta * tax, 2)
            else:
                amount = tax
            salary -= delta

    return round(amount, 2)

def get_payroll_tax(salary):
    constantsPayrollTax = [
    {"bracket":1,"min":0,"max":38097,"rate":0.0932},
    {"bracket":2,"min":38098,"max":75517,"rate":0.3697},
    {"bracket":3,"min":75518,"rate":0.495}]
    return get_rates(constantsPayrollTax, salary, "rate")

def get_social_tax(salary):
    constantsSocialPercent = [{"bracket":1,"min":0,"max":38097,"rate":0.3697,"social":0.2765,"older":0.0975}]
    return get_rates(constantsSocialPercent, salary, "social")

def get_general_credit(salary):
    constantsGeneralCredit = [
    {"bracket":1,"min":0,"max":24813,"rate":3362},
    {"bracket":2,"min":24813,"max":75518,"rate":-0.06630},
    {"bracket":3,"min":75519,"rate":0}]
    general_credit = get_rates(constantsGeneralCredit, salary, "rate")
    return general_credit

def get_labour_credit(salary):
    constantsLowWageThreshold = 9094
    constantsLabourCredit = [
    {"bracket":1,"min":0,"max":11490,"rate":0.08425},
    {"bracket":2,"min":11490,"max":24820,"rate":0.31433},
    {"bracket":3,"min":24820,"max":39957,"rate":0.02471},
    {"bracket":4,"min":39957,"max":124934,"rate":-0.06510},
    {"bracket":5,"min":115296,"rate":0}]
    if salary < constantsLowWageThreshold:
        return 0
    return get_rates(constantsLabourCredit, salary, "rate")





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