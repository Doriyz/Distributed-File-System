

class info:
    def __init__(self, name):
        self.name = name


test = dict()
test[1] = info('test1')
test[2] = info('test2')

print(test[1].name)
print(test[2])

test.pop(1)
# print(test[1].name)

for t in test: # loop index
    print(t)
    print(test[t].name)