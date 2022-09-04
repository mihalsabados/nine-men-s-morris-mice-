
#https://www.youtube.com/watch?v=9HFbhPscPU0&t=309s    + modifikovan
class HashMap:
    def __init__(self):
        self.size = 7
        self.map = [None] * self.size

    def _get_hash(self, key):
        if key > 66 or key % 10 > 6:
            raise IndexError("bad key!!!")
        return key // 10

    def __setitem__(self, key, value):
        key_hash = self._get_hash(key)
        key_value = [key, value]

        if self.map[key_hash] is None:
            self.map[key_hash] = list([key_value])
            return True
        else:
            for pair in self.map[key_hash]:
                if pair[0] == key:
                    pair[1] = value
                    return True
            self.map[key_hash].append(key_value)
            return True

    def __getitem__(self, key):
        key_hash = self._get_hash(key)
        if self.map[key_hash] is not None:
            for pair in self.map[key_hash]:
                if pair[0] == key:
                    return pair[1]
        return None

    def __delitem__(self, key):
        key_hash = self._get_hash(key)
        if self.map[key_hash] is None:
            return False
        for i in range(0, len(self.map[key_hash])):
            if self.map[key_hash][i][0] == key:
                self.map[key_hash].pop(i)
                if len(self.map[key_hash]) == 0:
                    self.map[key_hash] = None
                return True
        return False

    def keys(self):
        key_list = []
        for bucket in self.map:
            if bucket is not None:
                for pair in bucket:
                    key_list.append(pair[0])
        return key_list

    def values(self):
        values = []
        for bucket in self.map:
            if bucket is not None:
                for pair in bucket:
                    values.append(pair[1])
        return values

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        if key in self.keys():
            return True
        return False

    def __iter__(self):
        for bucket in self.map:
            if bucket is not None:
                for item in bucket:
                    yield item[0]


if __name__ == '__main__':
    h = HashMap()
    h[0] = "W"
    h[3] = "W"
    h[6] = "W"

    b = HashMap()
    b[0] = "W"
    b[3] = "W"
    b[6] = "W"
    print(h == b)


