import module

def process(img,unique_encoded,unique_faces,today,init_len):
    faces = []
    encode = face_recognition.face_encodings(img)
    face_locations = face_recognition.face_locations(img)

    # create the buffer for each face location and extract the face from the image
    for loc in face_locations:
        top, right, bottom, left = module.buffer(img, loc)
        face = img[top:bottom, left:right]
        faces.append(face)

    unique_faces, unique_encoded, today = module.process_image(unique_encoded,
                                                               unique_faces,
                                                               encode, faces,
                                                               today)

    print(f"{i} completed, {len(encode)} faces")
    i = i + 1

    print(f"Done. {len(unique_encoded) - init_len} new faces")

    return(unique_encoded,unique_faces,today,init_len)