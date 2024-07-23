'''Wizard for teaching task.'''

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui


class TeachTaskWizard(QtGui.QWizard):
    '''description of class'''

    def __init__(self) -> None:
        '''Init blah blah blah.'''

        super(TeachTaskWizard, self).__init__()

        self.setWindowTitle('How to use our software')
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(
            'resources/wizird.jpg'))
        self.number_of_pages = 1
        # Probably not needed.
        self.list_of_page_names = []
        self.list_of_page_functions = [self.make_page_one]

        self._side_menu()
        self.show()

    def _side_menu(self:'TeachTaskWizard') -> None:
        '''Left side menu widget for this wizard.'''

        self._left_side_menu = QtGui.QWidget(self)
        self._left_side_menu.grid_layout = QtGui.QGridLayout(
            self._left_side_menu)
        self._left_side_menu.label = QtGui.QLabel('Stuff!')

        self._left_side_menu.grid_layout.addWidget(self._left_side_menu.label,
                                                   1, 1)

        self.setSideWidget(self._left_side_menu)

    def build_pages(self:'TeachTaskWizard') -> None:
        '''Opening page.'''

        for index in range(1, (self.number_of_pages + 1)):

            page_name = ('page_' + str(index))
            self.list_of_page_names.append(page_name)
            # The page will have the parent set when the page is added.
            setattr(self, page_name, QtGui.QWizardPage())
            setattr(self, (page_name + '.page_value'), index)

        for page in self.list_of_page_names:

            this_func = self.list_of_page_functions.pop(0)

            self.setPage(self.page.page_value, this_func())
            self.page.setTitle('Dual n-Back')

    def make_page_one(self:'TeachTaskWizard') -> None:
        '''Page one.'''

        pg_one_txt = 'Opening info!'

        self.page_1.setSubTitle('Introduction')

        # set title and all that.

        

