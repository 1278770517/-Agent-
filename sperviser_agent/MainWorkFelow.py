from langchain.chat_models import init_chat_model
from langgraph.constants import END, START
from langgraph.graph import StateGraph, MessagesState

from sperviser_agent.child_graph_agent import supervisor_agent, web_search, flight_booking_agent, hotel_booking_agent, \
    car_rental_booking_agent, excursion_booking_agent, memory
from sperviser_agent.fetch_user_info_node import get_user_info
init_chat_model
mian_workflow=(StateGraph(MessagesState)
               .add_node('get_user_infor',get_user_info)
               .add_node('supersiver',supervisor_agent,destinations=("research_agent", 'flight_booking_agent', 'hotel_booking_agent', 'car_rental_booking_agent', 'excursion_booking_agent' , END))
               .add_node('research_agent',web_search,destinations=(END,))
               .add_node('flight_booking_agent',flight_booking_agent,destinations=(END,))
               .add_node('hotel_booking_agent',hotel_booking_agent,destinations=(END,))
               .add_node('car_rental_booking_agent',car_rental_booking_agent,destinations=(END,))
               .add_node('excursion_booking_agent',excursion_booking_agent,destinations=(END,))
               .add_edge(START, 'fetch_user_info')
               .add_edge('fetch_user_info', 'supervisor')
               .compile(checkpointer=memory)
               )
