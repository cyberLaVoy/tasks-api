from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from todos_db import TODOS_DB
from passlib.hash import bcrypt
from http import cookies
import json, sys, datetime

import sessionStore
gSessionStore = sessionStore.SessionStore()

class Handler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.sendCookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        self.loadSession()

        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS") 
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        return

    def do_GET(self):
        self.loadSession()

        if self.path == "/todos":
            if "userID" in self.mSession:
                self.handleTODOSList()
            else:
                self.handle401()
        elif self.path[:7] == "/todos/":
            if "userID" in self.mSession:
                available = self.checkTODOID()
                if available:
                    self.handleTODORetrieve()
                else:
                    self.handle404("member")
            else:
                self.handle401()
        else:
            self.handle404("collection")
        return

    def do_POST(self):
        self.loadSession()

        if self.path == "/todos":
            if "userID" in self.mSession:
                self.handleTODOCreate()
            else:
                self.handle401()

        elif self.path =="/users":
            self.handleUserCreate()
        elif self.path == "/sessions":
            self.handleCreateSession()

        elif self.path == "puzzle":
            self.handlePuzzleAnalysis()

        else:
            self.handle404("collection")
        return
    
    def do_PUT(self):
        self.loadSession()
        if self.path[:7] == "/todos/":
            if "userID" in self.mSession:
                available = self.checkTODOID()
                if available:
                    self.handleTODOReplace()
                else:
                    self.handle404("member")
            else:
                self.handle401()
        else:
            self.handle404("collection")

    def do_DELETE(self):
        self.loadSession()

        if self.path[:7] == "/todos/":
            if "userID" in self.mSession:
                available = self.checkTODOID()
                if available:
                    self.handleTODODelete()
                else:
                    self.handle404("member")
            else:
                self.handle401()
        else:
            self.handle404("collection")

# Puzzles methods
def handlePuzzleAnalysis(self):
    parsed_body = self.getParsedBody()
    puzzle_image = parsed_body.get("puzzle_image")[0]
    print(puzzle_image)
    boardLayout = {"board_layout": "2s0n7s0n0n0n1s0n4s0n3s9s1s0n2s0n0n0n0n0n6s4s0n8s7s0n0n0n6s0n0n0n0n3s0n2s5s0n7s0n9s0n0n1s0n0n0n2s1s0n0n9s0n4s0n0n9s0n0n0n4s0n6s0n5s0n3s0n6s0n0n0n0n3s0n2s0n0n0n7s0n"}
    jsonData = json.loads(board_layout)
    self.send_response(201)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(bytes(jsonData, "utf-8"))



# TODOS methods
    
    def handleTODOReplace(self):
        db = TODOS_DB()
        parsed_body = self.getParsedBody()
        ID = str(self.path[7:])
        taskItem = db.getTODO(ID)[0]

        short_description = taskItem["short_description"]
        long_description = taskItem["long_description"]
        desired_completion_date = taskItem["desired_completion_date"]
        due_date = taskItem["due_date"]
        completion_status = taskItem["completion_status"]
        priority = taskItem["priority"]

        if parsed_body.get("short_description") != None:
            short_description = parsed_body["short_description"][0]
        if parsed_body.get("long_description") != None:
            long_description = parsed_body["long_description"][0]
        if parsed_body.get("priority") != None:
            priority = parsed_body["priority"][0]
        if parsed_body.get("desirder_completion_date") != None:
            desired_completion_date = parsed_body["desired_completion_date"][0]
            if not self.checkDateFormat(desired_completion_date):
                desired_completion_date = None
        if parsed_body.get("due_date") != None:
            due_date = parsed_body["due_date"][0]
            if not self.checkDateFormat(due_date):
                due_date = None

        db.replaceTODO(short_description, long_description, priority, 
                      desired_completion_date, due_date, 
                      completion_status, ID)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Update successful.", "utf-8"))

    def handleTODODelete(self):
        db = TODOS_DB()
        ID = str(self.path[7:])
        db = TODOS_DB()
        db.deleteTODO(ID)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Delete successful.", "utf-8"))

    def handleTODOCreate(self):
        parsed_body = self.getParsedBody()
        
        short_description = ""
        long_description = ""
        priority = "1"
        desired_completion_date = None
        due_date = None
        completion_status = "False"
        date_entered = datetime.datetime.today().strftime('%Y-%m-%d')

        if parsed_body.get("short_description") != None:
            short_description = parsed_body["short_description"][0]
        if parsed_body.get("long_description") != None:
            long_description = parsed_body["long_description"][0]
        if parsed_body.get("priority") != None:
            priority = parsed_body["priority"][0]
        if parsed_body.get("desirder_completion_date") != None:
            desired_completion_date = parsed_body["desired_completion_date"][0]
            if not self.checkDateFormat(desired_completion_date):
                desired_completion_date = None
        if parsed_body.get("due_date") != None:
            due_date = parsed_body["due_date"][0]
            if not self.checkDateFormat(due_date):
                due_date = None
        
        db = TODOS_DB()
        print(short_description, long_description, priority, 
                      desired_completion_date, due_date, 
                      date_entered, completion_status, self.mSession["userID"])
        db.createTODO(short_description, long_description, priority, 
                      desired_completion_date, due_date, 
                      date_entered, completion_status, self.mSession["userID"])

        self.send_response(201)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Post complete.", "utf-8"))

    def handleTODOSList(self):
        db = TODOS_DB()
        to_dos = db.getTODOS(self.mSession["userID"])
        self.sendJSONObject(to_dos, "tasks", 200)

    def handleTODORetrieve(self):
        ID = str(self.path[7:])
        db = TODOS_DB()
        to_do = db.getTODO(ID)
        self.sendJSONObject(to_do, "task_item", 200, True)

    def checkTODOID(self):
        ID = int(self.path[7:])
        db = TODOS_DB()
        return db.checkTODOID( ID, self.mSession["userID"] )


# USERS Methods

    def handleUserCreate(self):
        db = TODOS_DB()
        parsed_body = self.getParsedBody()

        email = parsed_body["email"][0]
        valid_email = False
        for i in range(len(email)):
            if email[i] == "@" and "." in email[i:]:
                valid_email = True

        taken = db.checkUserEmail(email)
        if taken and not valid_email:
            self.handle422()
        else:
            fname = parsed_body["fname"][0]
            lname = parsed_body["lname"][0]
            password = parsed_body["password"][0]

            encrypted_password = bcrypt.encrypt(password)
            password = ""

            db.createUSER(email, encrypted_password, fname, lname)

            self.send_response(201)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes("User Created.", "utf-8"))

# SESSIONS Methods

    def handleCreateSession(self):
        db = TODOS_DB()
        parsed_body = self.getParsedBody()
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        email_exists = db.checkUserEmail(email)
        if email_exists:
            auth_info = db.getUserAuthInfo(email)
            verified = bcrypt.verify(password, auth_info[0]["encrypted_password"])
            if verified:
                self.mSession["userID"] = auth_info[0]["rowid"]
                user = db.getUser(auth_info[0]["rowid"])
<<<<<<< HEAD
                self.sendJSONObject(user, "user", 201, True)
=======
                json_string = json.dumps(user)
                self.send_response(201)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(json_string, "utf-8"))
>>>>>>> c3e81db3295dc8332a2c2e6408c32dcd3d28089b
            else:
                self.handle401()
        else:
            self.handle401()
    def loadSession(self):
        self.loadCookie()
        if "sessionID" in self.mCookie:
            sessionID = self.mCookie["sessionID"].value
            sessionData = gSessionStore.getSession(sessionID)
            if sessionData is not None:
                self.mSession = sessionData
            else:
                sessionID = gSessionStore.createSession()
                self.mCookie["sessionID"] = sessionID
                self.mSession = gSessionStore.getSession(sessionID)
        else:
            sessionID = gSessionStore.createSession()
            self.mCookie["sessionID"] = sessionID
            self.mSession = gSessionStore.getSession(sessionID)
    def sendCookie(self):
        for morsel in self.mCookie.values():
            self.send_header("Set-Cookie", morsel.OutputString()) 
    def loadCookie(self):
        print(self.headers)
        if "Cookie" in self.headers:
            self.mCookie = cookies.SimpleCookie(self.headers["Cookie"]) 
        else:
            self.mCookie = cookies.SimpleCookie()

# General Mehtods
    def checkDateFormat(self, date_string):
        valid_date = True
        try:
            datetime.datetime.strptime(date_string, '%Y-%m-%d')
        except ValueError:
            valid_date = False
        return valid_date

    def getParsedBody(self):
        length = int(self.headers["Content-length"])
        body = self.rfile.read(length).decode("utf-8")
        parsed_body = parse_qs(body)
        return parsed_body

    def sendJSONObject(self, load, label, statusCode, singleItemRequest=False):
        jsonObject = {}
        # change datatypes of values to strings
        for i in range(len(load)):
            for key in load[i]:
                load[i][key] = str(load[i][key])
        if (singleItemRequest):
            load = load[0]
        jsonObject[label] = load
        json_string = json.dumps(jsonObject)
        self.send_response(statusCode)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json_string, "utf-8"))

    def handle404(self, memberORcollection):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        if memberORcollection == "collection":
            self.wfile.write(bytes("The resource you are atempting to access was not found.", "utf-8"))
        else:
            self.wfile.write(bytes("The ID in the path provided was not found.", "utf-8"))

    def handle422(self):
        self.send_response(422)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Invalid data entry.", "utf-8"))

    def handle401(self):
        self.send_response(401)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("This request requires user authetication.", "utf-8"))

def main():
    db = TODOS_DB()
    db.createTodosTable()
    db.createUsersTable()
    db = None

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, Handler)

    print("Listening...")
    server.serve_forever()
main()

