from dataclasses import dataclass
from socket import getaddrinfo

from nicegui import ui
from loader_job import poll_job, JobStatus
from typing import Any, Optional
import asyncio



#1. Model
@dataclass
class JobState:
    loader_profile: str = ""
    loader_property: str = ""
    loader_environment: str = "Setup_Loader"
    loader_endpoint: str = ""
    status_endpoint: str = ""
    loader_job_error : Optional[list] = ""
    loader_job_result : str = ""
    status: str = "Idle"
    status_log: Optional[ui.log] = None
    progress: float = 0.0
    is_running : bool = False
    setup_loader_Endpoint = "http://awe1ptstpeps01.aws.portico.org:9500/loader/job/multistepjob/v1/submitwithjson/LoaderJob"
    inno_loader_Endpoint = "http://awe1ptindeps01.aws.portico.org:9500/loader/job/multistepjob/v1/submitwithjson/LoaderJob"

    setup_job_status = "http://awe1ptstpeps01.aws.portico.org:9500/loader/job/v1/status"
    inno_job_status = f"http://awe1ptindeps01.aws.portico.org:9500/loader/job/v1/status"
    headers = {"accept": "*/*", "Content-Type": "application/json"}




#3. Controller
class JobController:
    def __init__(self, state: JobState):
        self.state = state

    def log(self, message: str):
        if self.state.status_log:
            self.state.status_log.push(message)

    async def execute_task(self):
        if not self.state.loader_profile:
            ui.notify(f"Specify a loader file...", type="warning")
            return

        if not self.state.loader_property:
            ui.notify(f"Specify a loader property...", type="warning")
            return

        self.state.is_running = True
        self.state.status = "Processing..."
        self.state.progress = 0.2

        if self.state.loader_environment == 'Setup_Loader':
            self.state.loader_endpoint  = self.state.setup_loader_Endpoint
            self.state.status_endpoint = self.state.setup_job_status

        elif self.state.loader_environment == 'Innodata_Loader':
            self.state.loader_endpoint = self.state.inno_loader_Endpoint
            self.state.status_endpoint = self.state.inno_job_status
        else:
            pass

        ui.notify(f"Selected environment {self.state.loader_environment} and endpoint {self.state.loader_endpoint}", type="positive")
        self.log(f"Selected environment {self.state.loader_environment}")
        json_data = {"configSourceType":"GIT", "propertyFileName":self.state.loader_property, "loaderProfileFileName":self.state.loader_profile}

        try:
            status = await poll_job(self.state.loader_endpoint, self.state.status_endpoint, self.state.headers, json_data, on_log=self.log)
            self.state.loader_job_result = status.job_result
            self.log(f"Job Status {self.state.loader_job_result}")
            # if self.state.loader_job_result == 'COMPLETED':
            #     self.state.status_log.push(f"Job Status {self.state.loader_job_result}")
            self.state.status = "Completed.."
        except RuntimeError as ex:
            self.state.loader_job_error = ex
            self.log(f"[RuntimeError] Job Failed : {self.state.loader_job_error}")
            self.state.status = "RuntimeError.."
        except Exception as ex:
            if "11001" in str(ex):
                self.log(f"[DNS Lookup Failed] Check your  VPN connection : {str(ex)}")
                self.state.status = "Connection Exception   "
            else:
                self.state.loader_job_error = ex
                self.log(f"[Exception] Job Failed : {self.state.loader_job_error}")
                self.state.status = "Unknown Exception"

        finally:
            self.state.is_running = False
            self.state.progress = 1.0



#2 View
def create_ui():
    state = JobState()
    controller = JobController(state)

    environments = ["Setup_Loader", "Innodata_Loader"]

    with ui.card().classes("w-full max-w-lg mx-auto p-6 shadow-md rounded-xl"):
        ui.label("Batch Loading Utility").classes("text-xl font-bold tracking-tight text-gray-800")
        # , on_change=lambda e: ui.notify(f"Selected {e.value}")
        ui.radio(environments, value="Setup_Loader").props("inline color=primary").bind_value(state, "loader_environment", backward=lambda env: env)
        ui.input("Loader Profile").bind_value(state,"loader_profile", backward=lambda profile: profile).classes("w-full")
        ui.input("Loader Property").bind_value(state, "loader_property", backward=lambda property: property).classes("w-full")

        with ui.row().classes("w-full item-center justify-between mt-4"):
            ui.label().bind_text_from(state, "status", backward=lambda s: f"Status: {s}").classes("text-sm text-gray-600 font-medium")
            state.status_log = ui.log(max_lines=16).classes("w-full h-40 font-mono whitespace-pre-wrap break-words")
        with ui.row().classes("w-full item-center justify-between mt-4"):

            ui.button("Start Job", on_click=controller.execute_task).bind_enabled_from(state, "is_running",
                                                                                       backward=lambda r: not r).props("unelevated_color=primary")

        ui.linear_progress().bind_value(state, "progress").classes("mt-4")







create_ui()
# Run as a local native-like desktop app window
ui.run(title="Portico Batch Loader", native=True, reload=False, port=8000)