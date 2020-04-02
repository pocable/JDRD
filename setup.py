import os
import json

if __name__ == "__main__":
    print("This will output all keys and information at the end to verify.")
    input("Please make sure no one is around. Press enter to continue to the prompts.")



    d_srv = input("Enter DLAPI Server IP: ")
    d_key = input("Enter DLAPI Key: ")
    j_server = input("Enter Jackett Sever IP: ")
    j_key = input("Enter Jackett API Key: ")
    m_loc = input("Enter movie dl location (/movies/): ")
    tv_loc = input("Enter tv dl loction (/tv/): ")
    print("\n\n")

    f = open("keys.txt", 'w')
    toSave = {'DLAPI_SERVER': d_srv, 'DLAPI_KEY': d_key, 'JACKETT_SERVER': j_server, 'JACKETT_KEY': j_key, 'MOVIE_OUTPUT':m_loc, 'TV_OUTPUT':tv_loc}
    f.write(json.dumps(toSave))
    f.close()


    print("Saved configuration. Verify all information below: ")
    print("DLAPI IP: %s" % d_srv)
    print("DLAPI KEY: %s" % d_key)
    print("Jackett IP: %s" % j_server)
    print("Jackett KEY: %s" % j_key)
    print("Movie Path: %s" % m_loc)
    print('TV Path: %s' % tv_loc)

