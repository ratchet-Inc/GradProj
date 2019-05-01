import sys
import time

def CreateTableQuery(data, params):
    if not params.get('-cl'):
        return '**ERROR: Table column data not set.'
    params['-cl'] = params['-cl'].split(',')
    if len(data) != len(params['-cl']):
        print("**ERROR: table definition length is invalid.")
        return ''
    #print('cl data:', params['-cl'])
    query = 'CREATE TABLE ' + params['-tn'].lower() + '(\n'
    for index in range(len(data)):
        params['-cl'][index] = params['-cl'][index].replace('vc', 'varchar')
        params['-cl'][index] = params['-cl'][index].replace('nn', 'NOT NULL')
        params['-cl'][index] = params['-cl'][index].replace('un', 'unique')
        params['-cl'][index] = params['-cl'][index].replace('pk', 'primary key')
        params['-cl'][index] = params['-cl'][index].replace('fk', 'foreign key')
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
            q += '"'+entryData[i].replace('"', '\"')+'"'
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

def mainFunc(params):
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
        pass
    s = "USE " + params['-db'].strip() + ";\n"
    outF.write(s.encode('utf-8'))
    s = "DROP TABLE IF EXISTS " + params['-tn'].strip() + ";\n"
    outF.write(s.encode('utf-8'))
    data = ReadData(tfPtr)
    print("filtered line[0]: %s\n" % data)
    tableInfo = CreateTableQuery(data, params)
    print("Query:-\n\n%s" % tableInfo)
    outF.write(tableInfo.encode('utf-8'))
    lineData = ReadData(tfPtr)
    print("Line read[0]: %s" % (lineData))
    print("Translating file...")
    start = time.time()
    while len(lineData) > 1:
        entryData = CreateInsertQuery(data, lineData, params)
        #print("Query:-\n\n%s" % entryData)
        outF.write(entryData.encode('utf-8'))
        lineData = ReadData(tfPtr)
        pass
    end = time.time()
    print("Translationg completed in %d seconds. file saved as: './%s'\n\n" % ( end - start, fn))
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
