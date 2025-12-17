class Collection:
    def __init__(self, idcollection, name_of_collection, total_pages):
        self.__idcollection = None
        self.__name_of_collection = None
        self.__total_pages = None
        self.__pages_list = []

        self.set_idcollection(idcollection)
        self.set_name_of_collection(name_of_collection)
        self.set_total_pages(total_pages)

    def get_idcollection(self):
        return self.__idcollection

    def get_name_of_collection(self):
        return self.__name_of_collection

    def get_total_pages(self):  
        return self.__total_pages
    
    def get_pages_list(self):
        return self.__pages_list

    def set_idcollection(self, idcollection):
        self.__idcollection = idcollection

    def set_name_of_collection(self, name_of_collection):
        self.__name_of_collection = name_of_collection

    def set_total_pages(self, total_pages):
        self.__total_pages = total_pages

    def set_pages_list(self, pages):
        self.__pages_list.append(pages)

    def remove_page(self, page_id):
        for p in self.__pages_list:
            if p.get_idpage() == page_id:
                self.__pages_list.remove(p)
                return True
        return False
    
    