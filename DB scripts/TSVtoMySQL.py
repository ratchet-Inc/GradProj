import sys
import time

FilterKeyIndex = 0

def FilterKey(arr):
    k = arr[FilterKeyIndex].replace('tt', '0')
    k = k.replace('nm', '0')
    return int(k)

def FilterKey2(arr, index):
    k = arr[index].replace('tt', '0')
    k = k.replace('nm', '0')
    return int(k)

def CreateTableQuery(data, params):
    if not params.get('-cl'):
        print('**ERROR: Table column data not set.')
        return -1   
    params['-cl'] = params['-cl'].split(',')
    if len(data) != len(params['-cl']):
        print("**ERROR: table columns definition length is invalid: %s != %s" % (len(data), len(params['-cl'])))
        return -1
    #print('param data:', params['-cl'])
    #print('table data:', data)
    query = 'CREATE TABLE ' + params['-tn'].lower() + '(\n'
    for index in range(len(data)):
        params['-cl'][index] = params['-cl'][index].replace('.', ',')
        params['-cl'][index] = params['-cl'][index].replace('vc', 'varchar')
        params['-cl'][index] = params['-cl'][index].replace('nn', 'NOT NULL')
        params['-cl'][index] = params['-cl'][index].replace('un', 'unique')
        params['-cl'][index] = params['-cl'][index].replace('pk', 'primary key')
        params['-cl'][index] = params['-cl'][index].replace('fk', 'REFERENCES')
        if "references" in params['-cl'][index].lower():
            params['-cl'][index] += ' ' + params['-flt'][5].strip() + '(' + params['-flt'][6].strip() + ')'
            pass
        query += data[index].lower() + '_ ' + params['-cl'][index].strip()
        if index < (len(data) - 1):
            query += ',\n'
            pass
        pass
    return query+');\n'

def CreateInsertQuery(tableData, entryData, params):
    #print("tabelData:", tableData)
    q = 'insert into ' + params['-tn'] + '('
    for i in range(len(tableData)):
        q += tableData[i] + "_"
        if i != (len(tableData) - 1):
            q += ', '
            pass
        pass
    q += ') values('
    for i in range(len(entryData)):
        if 'varchar' in params['-cl'][i]:
            temp = entryData[i].replace('\"', "'")
            q += '"' + temp.replace('"', '\\"') + '"'
        else:
            q += entryData[i]
        if i != (len(entryData) - 1):
            q += ', '
            pass
        pass
    q += ');\n'
    q = q.replace('\\N', '-1')
    return q

def ReadData(filePointer):
    line = filePointer.readline().strip()
    line = line.decode().replace(' ', '_')
    line = line.replace('\t', ' ')
    l = line.split(' ')
    for i in range(len(l)):
        l[i] = l[i].replace("_", " ")
        pass
    return l

def FilterRead(ptr):
    line = ptr.readline()
    return line

def mainFunc(params):
    global FilterKeyIndex
    if not params.get('-tf') or not params.get('-of'):
        print("Target file or output file not set.")
        return -1
    try:
        tfPtr = open(params['-tf'], "rb")
    except:
        print("Exception caught: Failed to open target file.")
        return -1
    fn = params['-of'].strip()+"("+params['-tn'].strip()+")"
    outF = open("./"+fn+".sql", "wb+")
    if params['-ndb'].strip() == 'true':
        print("drop previous DB found!")
        s = "DROP DATABASE IF EXISTS " + params['-db'].strip() + ";\n"
        outF.write(s.encode('utf-8'))
        s = "CREATE DATABASE " + params['-db'].strip() + ";\n"
        outF.write(s.encode('utf-8'))
        pass
    s = "USE " + params['-db'].strip() + ";\n"
    outF.write(s.encode('utf-8'))
    s = "DROP TABLE IF EXISTS " + params['-tn'].strip() + ";\n"
    outF.write(s.encode('utf-8'))
    #print("filters(unparsed):", params.get('-flt'))
    params['-flt'] = params['-flt'].strip().split(',')
    print("filters(parsed):", params.get('-flt'))
    refPtr = None
    if int(params['-flt'][0].strip()) >= 2 and params['-flt'][1].strip() != 'none':
        refPtr = open('./'+params['-flt'][1].strip(), 'rb')
        pass
    if params['-flt'][0] == '3' or params['-flt'][0] == '1':
        FilterKeyIndex = int(params['-flt'][2].strip())
        print("Filtering at index:", FilterKeyIndex)
        pass
    data = ReadData(tfPtr)
    print("filtered line[0]: %s\n" % data)
    tableInfo = CreateTableQuery(data, params)
    if tableInfo == -1:
        return -1
    print("Query:-\n\n%s" % tableInfo)
    outF.write(tableInfo.encode('utf-8'))
    lineData = ReadData(tfPtr)
    print("Line read[0]: %s" % (lineData))
    print("Translating file...")
    entryData = CreateInsertQuery(data, lineData, params)
    print("Query:-\n\n%s" % entryData)
    #return -1
    filterBuffer = []
    endFiltering = False
    start = time.time()
    while len(lineData) > 1:
        entryData = CreateInsertQuery(data, lineData, params)
        if entryData == -1:
            return -1
        #print("Query:-\n\n%s" % entryData)
        if params['-flt'][0].strip() == '0':
            #print("no filtering")
            outF.write(entryData.encode('utf-8'))
            pass
        elif params['-flt'][0].strip() == '1' and params['-flt'][1].strip() in lineData[int(params['-flt'][3].strip())]:
            #print("filtering")
            outF.write(entryData.encode('utf-8'))
            filterBuffer.append(lineData)
            pass
        elif int(params['-flt'][0].strip()) >= 2:
            #print("semi filtering")
            if refPtr == None:
                print("*ERROR: Failed to open filter reference file.")
                return -1
            sLine = FilterRead(refPtr)
            if len(sLine) <= 2:
                print("quitting filtering due to keys being compared are greater than filter file keys")
                endFiltering = True
                pass
            while len(sLine) > 1:
                temp = sLine.decode().strip().split('||')
                index1 = int(params['-flt'][3].strip())
                index2 = int(params['-flt'][4].strip())
                temp[index1] = temp[index1].replace("'", '')
                #print("comparing: %s and %s" % (temp[index1], lineData[index2].strip()))
                if temp[index1].strip() == lineData[index2].strip().replace("'", ''):
                    #print("matched")
                    outF.write(entryData.encode('utf-8'))
                    if params['-flt'][0].strip() == '3':
                        filterBuffer.append(lineData)
                        pass
                    break
                elif FilterKey2(temp, index1) > FilterKey2(lineData, index2):
                    #print("comparing: %s and %s" % (temp[index1], lineData[index2].strip()))
                    #print("stopping search")
                    break
                sLine = FilterRead(refPtr)
                pass
            refPtr.seek(len(sLine) * -1, 1)
            if endFiltering:
                break
            pass
        else:
            #print("unknown filtering: %s and %s" % (params['-flt'][1], lineData[FilterKeyIndex]))
            pass
        lineData = ReadData(tfPtr)
        pass
    end = time.time()
    print("Translating completed in %d seconds. file saved as: './%s.sql'\n\n" % ( end - start, fn))
    if filterBuffer != []:
        print("**Starting filtering of file..")
        start = time.time()
        filterBuffer.sort(key = FilterKey)
        filterPtr = open('filtered(' + params['-tn'].strip() + ').txt', 'wb')
        for i in filterBuffer:
            s = ""
            for j in range(len(i)):
                s += str(i[j])
                if j != len(i) - 1:
                    s += " || "
                    pass
                pass
            s += '\n'
            filterPtr.write(s.encode('utf-8'))
            pass
        end = time.time()
        print("Filtering and ordering of file complete. Time taken: %d" % (end - start))
        filterPtr.close()
        pass
    print("\n\n**Executed completed succesfully.")
    tfPtr.close()
    outF.close()
    return 0

def ParseArgs():
    args = {}
    if len(sys.argv) > 1:
        curKey = ''
        for i in range(len(sys.argv)):
            if '-' in sys.argv[i]:
                curKey = sys.argv[i]
                args.update({curKey: ''})
                pass
            else:
                if curKey != '':
                    args[curKey] += sys.argv[i]+' '
                    pass
                pass
            pass
        pass
    return args

if "__main__" == __name__:
    #print("args:", sys.argv)
    params = ParseArgs()
    r = mainFunc(params)
    print(r)
