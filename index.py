import json

# Load constants from JSON file
with open('./data.json') as f:
    constants = json.load(f)

def round_number(value, places=2):
    return round(value, places)

def get_holiday_allowance(gross_year):
    return round_number(gross_year * 0.08 / 1.08) # Vakantiegeld (8%)

def get_tax_free_percentage(tax_free_year, gross_year):
    return round_number(tax_free_year / gross_year * 100)

def get_net_year(taxable_year, income_tax, tax_free_year):
    return round(taxable_year + income_tax + tax_free_year)

def get_amount_month(amount_year):
    return round_number(amount_year / 12)

def get_amount_week(amount_year):
    return round_number(amount_year / constants['workingWeeks'])


def get_amount_day(amount_year):
    return round_number(amount_year / constants['workingDays'])


def get_amount_hour(amount_year, hours):
    return round_number(amount_year / (constants['workingWeeks'] * hours))


def get_ruling_income(year, ruling):
    """
    30% Ruling (30%-regeling)
    https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/internationaal/werken_wonen/tijdelijk_in_een_ander_land_werken/u_komt_in_nederland_werken/30_procent_regeling/voorwaarden_30_procent_regeling/u-hebt-een-specifieke-deskundigheid

    @param {string} year Year to retrieve information from
    @param {string} ruling Choice between scientific research workers, young professionals with Master's degree or others cases
    @returns {number} The 30% Ruling minimum income
    """
    return constants['rulingThreshold'][str(year)][ruling]


def get_rates(brackets, salary, kind, multiplier=1):
    amount = 0
    for bracket in brackets:
        delta = bracket.get('max', float('inf')) - bracket['min'] if bracket.get('max') else float('inf')
        tax = round(multiplier * (bracket.get(kind, bracket["rate"])) * 100000) / 100000
        is_percent = -1 < tax < 1 and tax != 0

        if salary <= delta or not bracket.get('max'):
            if is_percent:
                calculated_amount = round_number(salary * tax, 2)
                amount += calculated_amount
            else:
                amount = tax  # This seems incorrect for fixed amounts; original logic might need revisiting.
            break  # Exit the loop as in JS logic with 'some'
        else:
            if is_percent:
                amount += round_number(delta * tax, 2)
            else:
                amount = tax  # This assignment might not align with expectations for continuous brackets.
            salary -= delta

    return round_number(amount, 2)





def get_payroll_tax(year, salary):
    return get_rates(constants['payrollTax'][str(year)], salary, "rate")

def get_social_tax(year, salary, older):
    """
    Calculates the social tax based on the given year, salary, and age category.
    Utilizes different rate brackets for "older" individuals versus others,
    as defined in the constants data structure.

    :param year: Year to retrieve information from.
    :param salary: Taxable wage that will be used for calculation.
    :param older: Boolean indicating if the individual is considered "older" for tax purposes.
    :return: The social tax amount after calculating the proper bracket amount.
    """
    # Choosing the correct key based on the 'older' flag
    key = "older" if older else "social"
    # Assuming 'constants' is a dictionary containing 'socialPercent' for various years
    return get_rates(constants['socialPercent'][str(year)], salary, key)

def get_general_credit(year, salary, older, multiplier=1):
    """
    Calculates the general tax credit based on the given year, salary, and age status.
    An additional credit is applied for workers who have reached retirement age.
    The calculation can be adjusted by a multiplier.

    :param year: Year to retrieve tax credit information from.
    :param salary: Taxable wage that will be used for calculation.
    :param older: Boolean indicating if the individual is considered "older" for tax purposes.
    :param multiplier: Scalar value to multiply against the final result (default is 1).
    :return: The general tax credit amount after calculations.
    """
    # Calculate the base general credit
    general_credit = get_rates(constants['generalCredit'][str(year)], salary, "rate", multiplier)
    
    # Additional credit for workers that have reached retirement age
    if older:
        general_credit += get_rates(constants['elderCredit'][str(year)], salary, "rate")
    
    return general_credit

def get_labour_credit(year, salary, multiplier=1):
    """
    Calculates the labor tax credit for a given year and salary.
    A low wage threshold is considered, below which no credit is applied.
    The calculation can be adjusted by a multiplier.

    :param year: Year to retrieve labor credit information from.
    :param salary: Taxable wage that will be used for calculation.
    :param multiplier: Scalar value to multiply against the final result (default is 1).
    :return: The labor tax credit amount after calculations.
    """
    # Check against the low wage threshold; no credit if salary is below the threshold
    if salary < constants['lowWageThreshold'][str(year)] / multiplier:
        return 0
    # Calculate the labor credit if salary is above the threshold
    return get_rates(constants['labourCredit'][str(year)], salary, "rate", multiplier)


def get_social_credit(year, older, social_security):
    """
    Calculates a social credit percentage based on age and social security coverage.
    This percentage adjusts the social contributions for the calculation of tax credits.

    JSON properties for socialPercent object:
    - rate: Higher full rate including social contributions to be used to get proportion
    - social: Percentage of social contributions (AOW + Anw + Wlz)
    - older: Percentage for retirement age (Anw + Wlz, no contribution to AOW)

    :param year: Year to retrieve social credit information from.
    :param older: Boolean indicating if the individual is considered "older" for tax purposes.
    :param social_security: Boolean indicating if the individual is covered by social security.
    :return: The calculated social credit percentage.
    """
    bracket = constants['socialPercent'][str(year)][0]
    percentage = 1  # Default percentage if social security is applicable

    if not social_security:
        # Calculate percentage by removing AOW + Anw + Wlz from total if not covered by social security
        percentage = (bracket['rate'] - bracket['social']) / bracket['rate']
    elif older:
        # Adjust percentage for older individuals by removing only AOW from total
        percentage = (bracket['rate'] + bracket['older'] - bracket['social']) / bracket['rate']

    return percentage



def calculate_salary_paycheck(salary_input, start_from, year, ruling):
    paycheck = {}

    paycheck['gross_year'] = paycheck['gross_month'] = paycheck['gross_week'] = paycheck['gross_day'] = paycheck['gross_hour'] = 0
    paycheck[f'gross_{start_from.lower()}'] =  salary_input['income']
    gross_year = paycheck['gross_year'] + paycheck['gross_month'] * 12 + paycheck['gross_week'] * constants['workingWeeks']
    gross_year += paycheck['gross_day'] * constants['workingDays'] + paycheck['gross_hour'] * constants['workingWeeks'] * salary_input['hours']
    gross_year = max(gross_year, 0)

    paycheck['gross_allowance'] = get_holiday_allowance(gross_year) if salary_input['allowance'] else 0
    paycheck['gross_year'] = round_number(gross_year)
    paycheck['gross_month'] = get_amount_month(gross_year)
    paycheck['gross_week'] = get_amount_week(gross_year)
    paycheck['gross_day'] = get_amount_day(gross_year)
    paycheck['gross_hour'] = get_amount_hour(gross_year, salary_input['hours'])

    paycheck['tax_free_year'] = 0
    paycheck['taxable_year'] = gross_year - paycheck['gross_allowance']
    if ruling['checked']:
        ruling_income = get_ruling_income(year, ruling['choice'])
        effective_salary = max(paycheck['taxable_year'] * 0.7, ruling_income)
        reimbursement = paycheck['taxable_year'] - effective_salary
        if reimbursement > 0:
            paycheck['tax_free_year'] = reimbursement
            paycheck['taxable_year'] -= reimbursement
    
    paycheck['tax_free_year'] = round_number(paycheck['tax_free_year'])
    paycheck['get_tax_free_percentage'] = get_tax_free_percentage(paycheck['tax_free_year'], gross_year)
    paycheck['taxable_year'] = round_number(paycheck['taxable_year'])
    paycheck['payroll_tax'] = -1 * get_payroll_tax(year, paycheck['taxable_year'])
    paycheck['payroll_tax_month'] = get_amount_month(paycheck['payroll_tax'])
    paycheck['social_tax'] = -1 * get_social_tax(year, paycheck['taxable_year'], salary_input['older']) if salary_input['socialSecurity'] else 0
    paycheck['social_tax_month'] = get_amount_month(paycheck['social_tax'])
    paycheck['tax_without_credit'] = round_number(paycheck['payroll_tax'] + paycheck['social_tax'])
    paycheck['tax_without_credit_month'] = get_amount_month(paycheck['tax_without_credit'])
    social_credit = get_social_credit(year, salary_input['older'], salary_input['socialSecurity'])
    paycheck['labour_credit'] = get_labour_credit(year, paycheck['taxable_year'], social_credit)
    paycheck['labour_credit_month'] = get_amount_month(paycheck['labour_credit'])
    paycheck['general_credit'] = get_general_credit(year, paycheck['taxable_year'], salary_input['older'], social_credit)
    paycheck['general_credit_month'] = get_amount_month(paycheck['general_credit'])
    paycheck['tax_credit'] = round_number(paycheck['labour_credit'] + paycheck['general_credit'])
    paycheck['tax_credit_month'] = get_amount_month(paycheck['tax_credit'])
    paycheck['income_tax'] = round_number(paycheck['tax_without_credit'] + paycheck['tax_credit'])
    paycheck['income_tax_month'] = get_amount_month(paycheck['income_tax'])
    paycheck['net_year'] = paycheck['taxable_year'] + paycheck['income_tax'] + paycheck['tax_free_year']
    paycheck['net_allowance'] = get_holiday_allowance(paycheck['net_year']) if salary_input['allowance'] else 0
    paycheck['net_month'] = get_amount_month(paycheck['net_year'])
    paycheck['net_week'] = get_amount_week(paycheck['net_year'])
    paycheck['net_day'] = get_amount_day(paycheck['net_year'])
    paycheck['net_hour'] = get_amount_hour(paycheck['net_year'], salary_input['hours'])

    return paycheck

salary_input = {
    "income": 60000,
    "allowance": False,
    "older": False,
    "socialSecurity": True,
    "hours": 40,
    "ruling": {
        "checked": False,
        "choice": "others"
    }
}

paycheck = calculate_salary_paycheck(salary_input, "year", 2024, salary_input["ruling"])

#print(get_rates(constants['generalCredit']['2024'], 60000, "rate", 1))

print(paycheck['net_month'])