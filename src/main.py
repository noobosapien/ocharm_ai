import time
import sched
import datetime
from queue import Queue


from dotenv import load_dotenv

load_dotenv()


from models import User
from db_connection import get_db_session, SessionLocal
from engine.piedpiper_engine import Engine

from helpers.create_classifier_assistant import create_classifier_assistant
from helpers.create_frame_assistant import create_frame_assistant


from classes.task_frame import TaskFrame

from engine.core.client import Client


def callback(user_id: str, output: str) -> None:
    print(user_id, ": ", output, "\n\n\n")


def task_due(task: TaskFrame):
    print("Task: ", task.content, " is due at time: ", task.hour_due, ":", task.minute_due)


if __name__ == "__main__":

    

    engine = Engine()
    db = SessionLocal()
    user_state_dict = {}
    user_frames = {}

    client = Client(id="abc1234", callback=callback)
    engine.add_client(client)

    msg_queue = Queue(maxsize=0)

    query = input("How can I help you today?")

    if client.get_id() not in user_state_dict:
        classifier_assistant = create_classifier_assistant(engine, client, msg_queue)

        engine.add_agent(client, classifier_assistant)

        engine.add_message(client.get_id(), query)
        time.sleep(3)

        engine.remove_agent(client, agent=classifier_assistant)
        msg = msg_queue.get()

        user_state_dict[client.get_id()] = msg.classification
        print(msg.classification, msg.user_id, msg.content)

    # query the DB and authenticate whether the request can be performed
    user = db.query(User).filter(User.jid == msg.user_id).first()
    if not (user.authenticated_use & 1 << msg.classification):
        raise Exception("User not authorized to perform the action")

    # depending on the classification do the action
    # create the task agent and add it to the engine
    frame = None

    if client.get_id() not in user_frames:
        frame = TaskFrame()
        user_frames[client.get_id()] = frame
    else:
        frame = user_frames[client.get_id()]

    frame_assistant = create_frame_assistant(engine=engine, client=client, frame=frame)
    engine.add_agent(client, frame_assistant)

    scheduler = sched.scheduler(time.time, time.sleep)

    try:
        # switch classification
        match user_state_dict[client.get_id()]:
            case 1:
                print("Creating task")
                # 1: create
                # populate the fields of the frame with the user input
                # while frame is not completed ask for more information
                # add to the priority queue

                string = "edit current frame with the user input: " + query
                engine.add_message(client_id=client.get_id(), input=string)

                time.sleep(2)
                while engine.get_process_list_len() != 0:
                    time.sleep(1)

                print(frame.to_json())

                while (
                    frame.severity == -1
                    or frame.minute_due == -1
                    or frame.hour_due == -1
                    or frame.day_due == -1
                    or frame.month_due == -1
                    or frame.year_due == -1
                ):
                    missing = []

                    if frame.severity == -1:
                        missing.append("Severity")

                    if frame.minute_due == -1:
                        missing.append("Minute")

                    if frame.hour_due == -1:
                        missing.append("Hour")

                    if frame.day_due == -1:
                        missing.append("Day")

                    if frame.month_due == -1:
                        missing.append("Month")

                    if frame.year_due == -1:
                        missing.append("Year")

                    message = f"Please enter the missing values for: {missing}\n"

                    query += ", "
                    query += input(message)

                    string = (
                        f"edit current frame:{frame.to_json()} with the user input: "
                        + query
                    )
                    engine.add_message(client_id=client.get_id(), input=string)

                    time.sleep(2)
                    while engine.get_process_list_len() != 0:
                        time.sleep(1)

                    print(frame.to_json())
                    frame.check_complete()
                
                frame.complete = True # use check_complete

                if frame.is_complete():
                    task = frame.to_task()
                    task_time = datetime.datetime(frame.year_due, frame.month_due, frame.day_due, frame.hour_due, frame.minute_due)

                    scheduler.enterabs(task_time.timestamp(), 1, task_due, (task))
                    del user_frames[client.get_id()]
                    scheduler.run()

            case 2:
                # 2: read
                print("Reading task")

                pass

            case 3:
                # 3: update

                print("Updating task")
                pass

            case 4:
                print("Deleting task")

                # 4: delete

                pass

            case _:
                pass

    except Exception as e:
        print(e)
