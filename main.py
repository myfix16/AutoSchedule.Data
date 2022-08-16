from typing import List

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from token_manager import TokenManager
from selenium import webdriver
from selenium.webdriver.support.select import Select
import time
import re
import os


tm = TokenManager()
tm.load_key("./secret.key")

id = b'gAAAAABf-VFK9Ae3x75XwAgT1Cshv1ntOV-vuiK2vS_gGRdrkfa3TOGVkv2hclh-1Vvo5y21VPw_JWMvjTfzBwlwtOmJD4Jwig=='
pswd = b'gAAAAABi22s6CpwU-HKwBpdMT03GyBuYcTPrIoepnNq3OtbEoBvH-6IlZeu52kOi0JM5sMEh6ha6_zOyRwayMdR7dd7P9RFV2Q=='

# The path to a browser
# driver = webdriver.Chrome(r'/Applications/chromedriver')
driver = webdriver.Edge(
    r'C:\Program Files (x86)\Microsoft\Edge\DevDriver\msedgedriver.exe')
driver.implicitly_wait(2)
wait = WebDriverWait(driver, 10, 0.5)

# To the shopping cart
# driver.get('http://sis.cuhk.edu.cn:81/psp/csprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL?PORTALPARAM_PTCNAV=HC_SSR_SSENRL_CART_GBL2&EOPP.SCNode=HRMS&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=PT_PTPP_PORTAL_ROOT&EOPP.SCLabel=&FolderPath=PORTAL_ROOT_OBJECT.PORTAL_BASE_DATA.CO_NAVIGATION_COLLECTIONS.PT_PTPP_PORTAL_ROOT.ADMN_F201512291342098588791689.ADMN_F201601191916357876084613.ADMN_S201601191922427744232182&IsFolder=false')
driver.get('https://sis.cuhk.edu.cn/psp/csprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL?PORTALPARAM_PTCNAV=HC_SSR_SSENRL_CART_GBL2&EOPP.SCNode=HRMS&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=PT_PTPP_PORTAL_ROOT&EOPP.SCLabel=&FolderPath=PORTAL_ROOT_OBJECT.PORTAL_BASE_DATA.CO_NAVIGATION_COLLECTIONS.PT_PTPP_PORTAL_ROOT.ADMN_F201512291342098588791689.ADMN_F201601191916357876084613.ADMN_S201601191922427744232182&IsFolder=false')
language_select = Select(driver.find_element_by_xpath('//*[@id="ptlangsel"]'))
language_select.select_by_value('ENG')

# TODO: If use wait only, sometimes, the user id isn't entered correctly.
wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="userid"]')))
time.sleep(1)
driver.find_element_by_xpath(
    '//*[@id="userid"]').send_keys(tm.decrypt_message(id).decode())
driver.find_element_by_xpath(
    '//*[@id="pwd"]').send_keys(tm.decrypt_message(pswd).decode())
driver.find_element_by_xpath('//*[@id="login"]/div/div[1]/div[9]/input').click()
driver.switch_to_window(driver.current_window_handle)
driver.switch_to_frame(
    driver.find_element_by_xpath('//*[@id="ptifrmtgtframe"]'))

# select the radio button representing the term and click the continue button
driver.find_element_by_xpath('//*[@id="SSR_DUMMY_RECV1$sels$7$$0"]').click()
driver.find_element_by_xpath('//*[@id="DERIVED_SSS_SCT_SSR_PB_GO"]').click()

# Go to the search page and get classes html
wait.until(EC.presence_of_element_located(
    (By.XPATH, '//*[@id="DERIVED_REGFRM1_SSR_PB_SRCH"]')))
driver.find_element_by_xpath('//*[@id="DERIVED_REGFRM1_SSR_PB_SRCH"]').click()

wait.until(EC.presence_of_element_located(
    (By.XPATH, '//*[@id="SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3"]')))
# delete the click of show open class only
driver.find_element_by_xpath(
    '//*[@id="SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3"]').click()
# select undergraduate
Select(driver.find_element_by_xpath(
    '//*[@id="SSR_CLSRCH_WRK_ACAD_CAREER$2"]')).select_by_visible_text("Undergraduate")
class_search = Select(driver.find_element_by_xpath(
    '//*[@id="SSR_CLSRCH_WRK_SUBJECT$0"]'))

courses: List[str] = [select.text for select in class_search.options]

view_all_clicked: bool = False

selected_courses = courses[:]
# the bug of biology makes expanding items easier
# selected_courses.insert(0, "Accounting")
for course in selected_courses:
    class_search.select_by_visible_text(course)
    wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH"]')))
    time.sleep(2)
    # click search
    driver.find_element_by_xpath(
        '//*[@id="CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH"]').click()
    # time.sleep(5)
    try:
        WebDriverWait(driver, 5, 0.5).until_not(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH"]')))
        try:
            driver.find_element_by_xpath('//*[@id="#ICSave"]').click()
        except NoSuchElementException:
            pass
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="DERIVED_CLSRCH_DESCR200$0"]')))

        # click "view all" to show all available sessions
        # ! A bug of sis that after clicking 'viewall' in biology page, view all is enabled in every page.
        # ! Therefore, necessary adjustments are made here.
        if not view_all_clicked:
            elements = driver.find_elements_by_css_selector(
                "a[id^='$ICField106$hviewall$']")
            for i in range(len(elements)):
                # if the search has more than 50 result, after clicking continue, it need to find element again
                try:
                    elements[i].click()
                except StaleElementReferenceException:
                    elements = driver.find_elements_by_css_selector("a[id^='$ICField106$hviewall$']")
                    elements[i].click()
                # * temporary solution
                time.sleep(5)
            if course == "Accounting":
                view_all_clicked = True

        # save the html
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="CLASS_SRCH_WRK2_SSR_PB_MODIFY"]')))
        address = f"./pages/{course.replace(':',' ')}.html"
        with open(address, "w+", encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.find_element_by_xpath(
            '//*[@id="CLASS_SRCH_WRK2_SSR_PB_MODIFY"]').click()
    except TimeoutException:
        # next item
        pass
    wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="SSR_CLSRCH_WRK_SUBJECT$0"]')))
    class_search = Select(driver.find_element_by_xpath(
        '//*[@id="SSR_CLSRCH_WRK_SUBJECT$0"]'))

print("Done.")
