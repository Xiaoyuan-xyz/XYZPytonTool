

class Number:
    def __init__(self, integer: int, decimal: list[int]) -> None:
        self.integer = integer
        self.decimal = decimal


    def __str__(self) -> str:
        if self.integer >= 0:
            return str(self.integer) + ('-P' if len(self.decimal) > 0 else '') + '-P'.join(map(str, self.decimal))
        else:
            if len(self.decimal) > 0:
                return 'P' + '+P'.join(map(str, self.decimal))
            else:
                return '1'
    def __sub__(self, other: 'Number'):
        if other.integer >= 0:
            raise NotImplementedError()
        else:
            dec = []
            i = len(other.decimal) - 1
            j = len(self.decimal) - 1
            while i >= 0 and j >= 0:
                if other.decimal[i] == self.decimal[j]:
                    dec.append(other.decimal[i] - 1)
                    i -= 1
                    j -= 1
                elif other.decimal[i] < self.decimal[j]:
                    if len(dec) > 0 and self.decimal[j] == dec[-1]:
                        dec[-1] -= 1
                    else:
                        dec.append(self.decimal[j])
                    j -= 1
                else:
                    if len(dec) > 0 and other.decimal[i] == dec[-1]:
                        dec[-1] -= 1
                    else:
                        dec.append(other.decimal[i])
                    i -= 1
            while i >= 0:
                if len(dec) > 0 and other.decimal[i] == dec[-1]:
                    dec[-1] -= 1
                else:
                    dec.append(other.decimal[i])
                i -= 1
            while j >= 0:
                if len(dec) > 0 and self.decimal[j] == dec[-1]:
                    dec[-1] -= 1
                else:
                    dec.append(self.decimal[j])
                j -= 1
            
            
            if dec[-1] == 0:
                inte = self.integer - 1
                dec = dec[:-1]
            else:
                inte = self.integer
            return Number(inte, dec[::-1])


    def divide(self):
        if self.integer >= 0:
            raise NotImplementedError()
        return Number(-999, [it+1 for it in self.decimal])

    
    def value(self):
        if self.integer < 0:
            return self
        if self.integer == 0:
            if len(self.decimal) == 0: # f(0)=P1
                return Number(-999, [1])
            # f(-PA-PB) = PA+PB
            return Number(-999, self.decimal)
        if self.integer == 1:
            if len(self.decimal) == 0: # f(1)=P3
                return Number(-999, [3])
            if len(self.decimal) == 1: # f(1-PA) = P(A+1)
                return Number(-999, [self.decimal[0] + 1])
            # f(1-PA-PB-PC) = PB+PC
            return Number(-999, self.decimal[1:])
        if self.integer == 2:
            if len(self.decimal) == 0:
                return Number(-999, [10])
            if len(self.decimal) == 1:
                return Number(-999, [2 * self.decimal[0] + 3])  # f(2-PA) = P(2A+3)
            # f(2-PA-PB-...-PZ) = P(A+Z+3-n)
            return Number(-999, [self.decimal[0] + self.decimal[-1] + 3 - len(self.decimal)])
        if self.integer == 3:
            print(self)
            return (self - Number(2, self.decimal).value()).value().divide()
        raise NotImplementedError()

    def next(self):
        if self.integer != 3:
            raise NotImplementedError()
        if len(self.decimal) == 0:
            return Number(3, [10])  # f(3) = 1/2 f(3-P10)
        if len(self.decimal) == 1:
            return self - Number(-1, [2 * self.decimal[0] + 3])
        return self - Number(-999, [self.decimal[0] + self.decimal[-1] + 3 - len(self.decimal)])

if __name__ == '__main__':



    num = Number(3, [8])
    # print(num.value())
    i = 10
    while num.integer == 3:
        # print(num)
        num = num.next()
        i = i + 1
        # if i == 20:
        #     break
    print(i)