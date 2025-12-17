class Album:
    def __init__(self, idalbum, name_of_album):
        self.__idalbum = None
        self.__name_of_album = None
        self.__collection_list = [] 

        self.set_idalbum(idalbum)
        self.set_name_of_album(name_of_album)


    def get_collection_list(self):
        return self.__collection_list

    def get_idalbum(self):
        return self.__idalbum

    def get_name_of_album(self):
        return self.__name_of_album

    def set_idalbum(self, idalbum):
        self.__idalbum = idalbum

    def set_name_of_album(self, name_of_album):
        self.__name_of_album = name_of_album

    def set_collection_list(self, collection):
        self.__collection_list.append(collection)
    
    def remove_collection(self, collection_id):
        for c in self.__collection_list:
            if c.get_idcollection() == collection_id:
                self.__collection_list.remove(c)
                return True
        return False


