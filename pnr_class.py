import pnr_segment

class pax_name:
    def __init__(self, SurName, FirstName, TypePax, Quantity):
        
        self.SurName = SurName
        self.FirstName = FirstName
        self.TypePax = TypePax
        self.Quantity = Quantity
        

    def __str__(self):
        return f'{self.SurName} {self.FirstName} {self.TypePax} {self.Quantity}'


class pax_contact:
    def __init__(self, Type, Data):
        
        self.Type = Type
        self.Data = Data


    def __str__(self):
        return f'{self.Type} {self.Data}'


    def __eq__(self, other):
        return self.Type == other.Type and self.Data == other.Data


class pnr_class:
    def __init__(self, rloc, names, segments, contacts):
        
        self.rloc = rloc
        self.names = names
        self.segments = segments
        self.contacts = contacts


    def __str__(self):
        # intended for users:
        
        #names_str = segments_str = contacts_str = ''
        
        names_str = '\n'.join([str(name) for name in self.names])
        #for name in self.names:
        #    names_str += str(name) + '\n'
            
        segments_str = '\n'.join([str(segment) for segment in self.segments])
        #for segment in self.segments:
        #    segments_str += str(segment) + '\n'
            
        contacts_str = '\n'.join([str(contact) for contact in self.contacts])
        #for contact in self.contacts:
        #    contacts_str += str(contact) + '\n'
        
        return f'''rloc: {self.rloc}
{names_str}
{segments_str}
{contacts_str}
'''


    def __repr__(self):
        #intended for developers: can recreate the object by eval()
        #mydate1 = datetime.datetime.now()
        #mydate2 = eval(repr(mydate1))
        #print("the values of the objects are equal: ", mydate1==mydate2)
        
        return f'pnr'
