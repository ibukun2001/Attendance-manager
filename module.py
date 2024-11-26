import psycopg2
import numpy as np
import pandas as pd
import face_recognition



def retrieve_from_db():
    """"
    Retrieves the data from the database as a dictionary and pandas dataframe
    returns: Dict,df
    """
    db_record = {
    'ID' :[],
    'name': [],
    'face': [],
    'face_encode' : []
    }
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        database="Attendance manager",
        user="postgres",
        password="password",
        port="5432"
    )

    # Create a cursor
    cur = conn.cursor()

    # Query to retrieve the binary image data and the shape
    cur.execute('SELECT id, name, Face BYTEA, image_shape, db_encode FROM GeneralAttendance')  # Adjust to get the correct row
    result = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()


    for row in result:
        db_record['ID'].append(row[0])
        db_record['name'].append(row[1]) 
        db_record['face_encode'].append(np.fromstring(row[4].strip("[]"), sep=" "))
        binary_data = row[2]  # The binary image data (BYTEA)
        image_shape = eval(row[3])  # Convert the image shape from text to tuple

        binary_data = bytes.fromhex(binary_data[2:])
        image_data = np.frombuffer(binary_data, dtype=np.uint8)
        face = image_data.reshape(image_shape)
        db_record['face'].append(face)

    return db_record

def buffer(img,face_loc):
    '''
    The buffer function refines the detected face location by 
    enlarging it so that the full face can be extcracted
    '''
    top,right,bottom,left = face_loc
    h,w = [bottom-top ,right-left]
    h,w = [int(0.2*side) for side in [h,w]]

    top = max(0, top-2*h)
    bottom = min(img.shape[0], bottom+h)
    left = max(0, left-w)
    right = min(img.shape[1], right+w)
    
    return(top,right,bottom,left)

def process_image(unique_encoded, unique_faces,encode,faces,today):
    '''
    :param unique_encoded:
    :param unique_faces:
    :param today:
    :return:
    '''
    #if we have an empty list for unique faces, update it with the newly encoded
    if len(unique_encoded)== 0:
        unique_encoded = encode
        unique_faces = faces
        print(f"INITIAL UPDATE. {len(unique_encoded)} faces")

    # Else, check if it matches any in the DB or today's faces, mark present or leave absent
    else:
        for n in range(0,len(encode)):
            matches = face_recognition.compare_faces(unique_encoded, encode[n],0.4)
            #if no true value is found in matches, update as unique
            if not any(matches):
                #unique_encoded.append(encode[n])
                unique_encoded = np.concatenate((unique_encoded,[encode[n]]))
                unique_faces.append(faces[n])
                today.append(True)
                
            #if any true value is found in matches(It matches faces in our record), feed another separate list
            if any(matches):
                dist = face_recognition.face_distance(unique_encoded, encode[n])
                #close_idx = dist.index(min(dist))
                close_idx = np.argmin(dist)  # Use np.argmin to get the index of the minimum value
                #dbase.iloc[close_idx][date] = True
                today[close_idx] = True

    return unique_faces,unique_encoded,today


def update_database(unique_encoded,unique_faces,today,date,init_len):
    date = 'D25_10_2024'

    # Assuming unique_faces and unique_encoded are available
    im_byte = []
    im_size = []

    ## Get only the encoded faces for today
    if init_len > 0:
        todays_faces = unique_faces[init_len-1:]
        todays_encoded = unique_encoded[init_len-1:]
    else:
        todays_faces = unique_faces
        todays_encoded = unique_encoded
    
    #Convert each face image array to binary
    for face in todays_faces:
        im_byte.append(psycopg2.Binary(face.tobytes()))  # Convert face to binary format
        im_size.append(face.shape)
        
    # Structure the data in a pandas dataframe
    df = pd.DataFrame({
        'names': [None] * len(todays_faces),  # Create an empty list for the names
        'Face': im_byte,
        'image_shape': list(im_size),
        'db_face': list(todays_faces),
        'db_encode': list(todays_encoded)
    })

    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        database="Attendance manager",
        user="postgres",
        password="password",
        port="5432"
    )

    # Create a cursor
    cur = conn.cursor()

    # Create a table in the database (adjust SQL to your needs)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS GeneralAttendance (
        id SERIAL PRIMARY KEY,
        name TEXT,
        Face BYTEA,  -- Store the face image as binary (BYTEA)
        image_shape TEXT,  -- Store shape as text, adjust if needed
        db_encode TEXT
    )
    ''')

    # Iterate over DataFrame rows and insert them into the table one by one
    for i, row in df.iterrows():
        cur.execute(
            "INSERT INTO GeneralAttendance (name, Face, image_shape, db_encode) VALUES (%s, %s, %s, %s)",
            (row['names'], row['Face'], str(row['image_shape']), str(row['db_encode']))
        )

    # Create the new column for the date attendance(if not existing) and update it
    cur.execute(f"""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                    WHERE table_name='generalattendance' 
                    AND column_name='{date}') THEN
            ALTER TABLE GeneralAttendance ADD COLUMN {date} BOOLEAN;
        END IF;
    END $$;
    """)

    # Update rows with the values from the 'today' list
    for i, value in enumerate(today):
        cur.execute(f"""
        UPDATE GeneralAttendance
        SET {date} = %s
        WHERE ctid = (SELECT ctid FROM GeneralAttendance ORDER BY ctid LIMIT 1 OFFSET %s);
        """, (value, i))



    # Commit changes and close the connection
    conn.commit()
    cur.close()
    conn.close()

