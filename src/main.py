from engine.core.client import Client
from classes.task_frame import TaskFrame
from helpers.create_frame_assistant import create_frame_assistant
from helpers.create_classifier_assistant import create_classifier_assistant
from helpers.create_read_assistant import create_read_assistant
from managers.TaskManager import TaskManager
from engine.piedpiper_engine import Engine
from db_connection import get_db_session, SessionLocal
from models import User
import time
from queue import Queue
import traceback
import json


from dotenv import load_dotenv

load_dotenv()


def callback(user_id: str, output: str) -> None:
    print(user_id, ": ", output, "\n\n\n")


def task_due(content, hour, minute):
    print("Task: ", content, " is due at time: ", hour, ":", minute)


if __name__ == "__main__":

    engine = Engine()
    db = SessionLocal()
    user_state_dict = {}
    user_frames = {}

    task_manager = TaskManager(task_due)

    client = Client(id="abc1234", callback=callback)
    engine.add_client(client)

    msg_queue = Queue(maxsize=0)

    query = input("How can I help you today?")

    if client.get_id() not in user_state_dict:
        classifier_assistant = create_classifier_assistant(
            engine, client, msg_queue)

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

    try:
        # switch classification
        match user_state_dict[client.get_id()]:
            case 1:
                print("Creating task")
                # 1: create
                # populate the fields of the frame with the user input
                # while frame is not completed ask for more information
                # add to the priority queue

                # depending on the classification do the action
                # create the task agent and add it to the engine
                frame = None

                if client.get_id() not in user_frames:
                    frame = TaskFrame()
                    user_frames[client.get_id()] = frame
                else:
                    frame = user_frames[client.get_id()]

                frame_assistant = create_frame_assistant(
                    engine=engine, client=client, frame=frame)

                engine.add_agent(client, frame_assistant)

                string = "edit current frame with the user input: " + query
                engine.add_message(client_id=client.get_id(), input=string)

                time.sleep(2)
                while engine.get_process_list_len() != 0:
                    time.sleep(1)

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

                    message = f"Please enter the missing values for: {
                        missing}\n"

                    query += ", "
                    query += input(message)

                    string = (
                        f"edit current frame:{
                            frame.to_json()} with the user input: "
                        + query
                    )
                    engine.add_message(client_id=client.get_id(), input=string)

                    time.sleep(2)
                    while engine.get_process_list_len() != 0:
                        time.sleep(1)

                    print(frame.to_json())
                    frame.check_complete()

                frame.complete = True  # use check_complete

                if frame.is_complete():
                    task = frame.to_task(client.get_id())

                    del user_frames[client.get_id()]

                    task_manager.add_task(task)

                    engine.remove_agent(client, agent=frame_assistant)
                    print("Created task for id: ", client.get_id())

            case 2:
                # 2: read
                print("Reading task")

                # Example Queries for reading:
                # * What is the next task?
                # * How many tasks are there for today?
                # * Has the previous task been completed?

                read_assistant = create_read_assistant(
                    engine=engine, client=client, task_manager=task_manager)

                engine.add_agent(client, read_assistant)

                string = "get the tasks from the input: " + query
                engine.add_message(client_id=client.get_id(), input=string)

                time.sleep(2)
                while engine.get_process_list_len() != 0:
                    time.sleep(1)

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

        while True:
            task_manager.get_queue_empty()
            msg = task_manager.poll_due_event()

            if msg == None:
                continue

            msg = json.loads(msg)

            match msg['type']:
                case 'sched_task':
                    print("\n\nTask due:\n\n")
                    print(msg)
                case 'sched_len':
                    if msg["length"] == 0:
                        task_manager.quit()
                        break

                case 'sched_next_task':
                    task_manager.set_next_task(msg['next_task'])

                case _:
                    pass

    except Exception as e:
        print("Main exception: ", e)
        traceback.print_exc()
