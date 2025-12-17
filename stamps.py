class Stamps:
    def __init__(self, idstamp, name_of_stamp, country, year, series):
        self.__idstamp = None
        self.__country = None
        self.__name_of_stamp = None
        self.__year = None 
        self.__series = None

        self.set_country(country)
        self.set_series(series)
        self.set_idstamp(idstamp)
        self.set_name_of_stamp(name_of_stamp)
        self.set_year(year)

    def get_idstamp(self):
        return self.__idstamp

    def get_name_of_stamp(self):
        return self.__name_of_stamp

    def get_country(self):
        return self.__country

    def get_year(self):
        return self.__year

    def get_series(self):
        return self.__series

    def set_idstamp(self, idstamp):
        self.__idstamp = idstamp

    def set_name_of_stamp(self, name_of_stamp):
        self.__name_of_stamp = name_of_stamp

    def set_country(self, country):
        self.__country = country
    
    def set_year(self, year):
        self.__year = year

    def set_series(self, series):
        self.__series = series