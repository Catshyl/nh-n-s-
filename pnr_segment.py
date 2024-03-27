class pnr_segment:

    def __init__(self, Qualifier, LineNum, DepDate, DepTime, ArrDate, ArrTime, FromCity, ToCity, Carrier, Flt, RBD, NumPax, Status):
        
        self.Qualifier = Qualifier
        self.LineNum = LineNum
        self.DepDate = DepDate
        self.DepTime = DepTime
        self.ArrDate = ArrDate
        self.ArrTime = ArrTime
        self.FromCity = FromCity
        self.ToCity = ToCity
        self.Carrier = Carrier
        self.Flt = Flt
        self.RBD = RBD
        self.NumPax = NumPax
        self.Status = Status


    def __str__(self):
        # intended for users:
        #  2  QH 219 Y 27NOV 1 HANSGN UN1          0700 0900
        return f'{self.Qualifier} {self.LineNum} {self.Carrier} {self.Flt} {self.RBD} {self.DepDate} {self.FromCity}{self.ToCity} {self.Status} {self.NumPax} {self.DepTime} {self.ArrTime}'