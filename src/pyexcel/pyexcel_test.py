import pyexcel as p

def main():
    records = p.get_records(file_name="classical_music_sample.xlsx")
    for record in records:
        print(f"{record['Representative Composers']} lived in {record['Period']} and belog to {record['Name']} period")

    print("")
    rows = p.get_array(file_name="classical_music_sample.xlsx", start_row=1)
    for row in rows:
        print(f"{row[2]} lived in {row[1]} and belog to {row[0]} period")

    print("")
    my_dict = p.get_dict(file_name="classical_music_sample.xlsx", name_columns_by_row=0)
    for (key,value) in my_dict.items():
        print(key)
        print(key + ": " + ' '.join([str(item) for item in value]))


if __name__=='__main__':
    main()
