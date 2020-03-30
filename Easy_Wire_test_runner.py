from pywinauto import Application
from pywinauto import application
from pywinauto import timings
from pywinauto import base_wrapper
from pathlib import Path
import time
import sys
import statistics


class EasyWire:
    """
    Class

    """

    def __init__(self, hv_status=True):
        self.title = u'Cirris Easy-Wire'
        self.test_category_name = 'EW - Test Time'
        self.class_name = 'TInitialDialog'
        self.ew_path = self.ew_get_path()
        self.app = self.start_ew()
        self.login(user='Master Login', tester_type='1100/Easy Touch', password='')
        self.app_uia = Application(backend='uia').connect(class_name_re='TInitialDialog')
        self.ew_test_list_window = self.app_uia[u'Cirris Easy-Wire'].child_window(class_name='TListView')
        self.test_list = []
        self.lv_test_time = []
        if hv_status:
            self.hv_status = True
            self.hv_test_time = []
        else:
            self.hv_status = False

    def __str__(self):
        return f'App is {self.app}, test list is {self.test_list}, lv_test_time is {self.lv_test_time}, ' \
               f'hv_time_test is {self.hv_test_time}, ew_path is {self.ew_path}'

    def __repr__(self):
        return f'App is {self.app}, test list is {self.test_list}, lv_test_time is {self.lv_test_time}, ' \
               f'hv_time_test is {self.hv_test_time}, ew_path is {self.ew_path}'

    def ew_get_path(self):
        """
        method to locate easywire install path

        :return: string of install path
        """
        install_dict = dict()
        possible_install_paths = [['ew_dev', Path(r'C:\Dev\PC\Cirris\EasyWire\PC\Project\easywire.broken.exe')],
                                  ['ew_64_install', Path(r'C:\Program Files (x86)\Cirris\easywire\easywire.exe')],
                                  ['ew_32_install', Path(r'C:\Program Files\Cirris\easywire\easywire.exe')]]
        for pair in possible_install_paths:
            install_dict[pair[0]] = pair[1]

        found = False
        for key, value in install_dict.items():
            if value.exists():
                found = True
                return str(value)

    def start_ew(self):
        """
        method to connect or launch easywire if not currently running

        :return: pywinauto Application object
        """

        try:
            app = Application().connect(title=self.title, class_name=self.class_name)
            return app
        except(application.ProcessNotFoundError, application.findwindows.ElementNotFoundError):
            app = Application().start(self.ew_path)
            return app

    def login(self, user='Master Login', tester_type='1100/Easy Touch', password=''):
        """
        method to log into easywire.

        :param user: User name required to log into easywire.  Defaults to 'Master Login'
        :param tester_type: Model type of the tester to be used during automated testing.  Defaults to 1100/Easy Touch
        :param password: Password required to login.  Defaults to ''
        :return: None
        """

        self.app.UserLogin.wait('ready')
        self.app.UserLogin.ComboBox.select(user)
        self.app.UserLogin.TEdit.set_text(password)

        try:
            self.app.UserLogin.ComboBox2.select(tester_type)
        except ValueError:
            pass

        self.app.Userlogin.OK.click()
        try:
            self.app.Hardware.wait('ready')
            print("Hardware error")
            print(self.app.Hardware.Edit.TextBlock())
            self.app.Hardware.OK.click()
        except timings.TimeoutError:
            pass

    def get_test_list(self, category_name='EW - Test Time'):
        """
        method to collect test list for a given category name in easywire.

        :param category_name: string of category name in easywire.  Defaults to 'Ew - Test Time'
        :return: list of tests from category name
        """
        test_list = []
        self.app[self.title].TComboBox.select(category_name)
        self.app_uia.window_(visible_only=False).restore()
        for test in self.ew_test_list_window.texts():
            if test[0].strip("'"):
                test_list.append(test[0])
        return test_list

    def select_current_test(self, test):
        """
        method to select current test from drop down list in easywire
        :param test: string of test name from easywire
        :return:
        """
        self.ew_test_list_window[test].select()
        try:
            self.app[self.title].Test.click()
        except base_wrapper.ElementNotEnabled:
            print('Tried to click Test button but it is not enabled')
            print('Verify the correct tester is attached and connected')
            sys.exit()

    def wait_helper(func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    value = func(*args, **kwargs)
                    return value
                except kwargs['exception_to_handle']:
                    print('Confirm Easy-Wire window has focus')
                    time.sleep(1)
                except:
                    time.sleep(1)
        return wrapper

    @wait_helper
    def confirm_lv_test_window_good(self, **kwargs):
        test_window_handle = kwargs['test_window_handle']
        start_time = time.time()
        test_window_handle.Start.click()
        test_window_handle.Good.wait('ready')
        end_time = time.time()
        return start_time, end_time

    @wait_helper
    def confirm_lv_hv_test_window_good(self, **kwargs):
        test_window_handle = kwargs['test_window_handle']
        start_time = time.time()
        test_window_handle.Start.click()
        test_window_handle.Hipot.wait('ready')
        hv_start = time.time()
        test_window_handle.Hipot.click()
        end_time = time.time()
        test_window_handle.Done.wait('ready')
        hv_stop = time.time()
        test_window_handle.Done.click()
        return start_time, end_time, hv_start, hv_stop

    def test_lv_only(self, test_iterations=3):
        self.test_list = self.get_test_list(category_name='EW - Test Time')
        for test_num, test in enumerate(self.test_list, 1):
            for x in range(1, test_iterations + 1):
                print(f'Test #{x} - Test name: {test}')
                self.select_current_test(test)
    #            while not self.app_uia.TTestWindow.Start.wait('ready'):
                test_window = self.app[f'Test Program - [{test} - Signature Single Test]']
                while True:
                    try:
                        test_window.Start.wait('ready')
                        break
                    except timings.TimeoutError:
                        print('timeout error triggered.')
                        time.sleep(1)
                lv_start = time.time()
                _, lv_stop = self.confirm_lv_test_window_good(test_window_handle=test_window,
                                                              exception_to_handle=timings.TimeoutError)
                test_window.Done.click()
                self.lv_test_time.append(round(lv_stop - lv_start, 3))
        self.maths()

    def test_lv_hv(self, test_iterations=3):
        self.test_list = self.get_test_list(category_name='EW - Time Test lvhv')
        for test_num, test in enumerate(self.test_list, 1):
            for x in range(1, test_iterations + 1):
                self.select_current_test(test)
                print(f'Test #{x} - Test name: {test}')
                test_window = self.app.window(title_re=".*" + test + ".*")
                lv_start, lv_stop, hv_start, hv_stop = self.confirm_lv_hv_test_window_good(test_window_handle=test_window,
                                                              exception_to_handle=timings.TimeoutError)
            self.lv_test_time.append(round(lv_stop - lv_start, 3))
            self.hv_test_time.append(round(hv_stop - hv_start, 3))
        self.maths()

    def maths(self):
        print(f'Baseline lv: {self.lv_test_time}')
        print(f'LV Values Median: {statistics.median(self.lv_test_time)}')
        print(f'LV Values Median_low: {statistics.median_low(self.lv_test_time)}')
        print(f'LV Values Median_high: {statistics.median_high(self.lv_test_time)}')

        if self.hv_status:
            print(f'Baseline hv: {self.hv_test_time}')
            print(f'HV Values Median: {statistics.median(self.hv_test_time)}')
            print(f'HV Values Median_low: {statistics.median_low(self.hv_test_time)}')
            print(f'HV Values Median_high: {statistics.median_high(self.hv_test_time)}')


E_lv_hv = EasyWire(hv_status=True)
E_lv_hv.test_lv_hv()