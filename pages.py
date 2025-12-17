class Pages:
    def __init__(self, idpages, number_of_page):
        self.__idpages = None
        self.__number_of_page = None
        self.__stamps_list = []

        self.set_idpage(idpages)
        self.set_number_of_page(number_of_page)

    def get_stamps_list(self):
        return self.__stamps_list

    def get_number_of_page(self):
        return self.__number_of_page

    def get_idpage(self):
        return self.__idpages

    def set_idpage(self, idpages):
        self.__idpages = idpages

    def set_number_of_page(self, number_of_page):
        self.__number_of_page = number_of_page

    def set_stamps_list(self, stamps):
        self.__stamps_list.append(stamps)
    
    def remove_stamp(self, stamp_id):
        for s in self.__stamps_list:
            if s.get_idstamp() == stamp_id:
                self.__stamps_list.remove(s)
                return True
        return False
