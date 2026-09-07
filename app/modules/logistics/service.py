from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


SHIPMENT_STATES = [
    "PENDING",
    "ASSIGNED",
    "PICKED_UP",
    "IN_TRANSIT",
    "DELIVERED",
    "CANCELLED",
]


ALLOWED_TRANSITIONS = {
    "PENDING": "ASSIGNED",
    "ASSIGNED": "PICKED_UP",
    "PICKED_UP": "IN_TRANSIT",
    "IN_TRANSIT": "DELIVERED",
}


class LogisticsService:

    def transition_shipment(self, shipment, next_status):
        current_status = shipment.status

        if current_status == next_status:
            raise ValueError(
                f"Shipment is already in {current_status} state"
            )

        expected_status = ALLOWED_TRANSITIONS.get(current_status)

        if expected_status != next_status:
            raise ValueError(
                f"Invalid transition: {current_status} -> {next_status}"
            )

        shipment.status = next_status
        return shipment

    def optimize_route(self, distance_matrix, start_index=0):
        if not distance_matrix:
            raise ValueError("Distance matrix cannot be empty")

        size = len(distance_matrix)

        if any(len(row) != size for row in distance_matrix):
            raise ValueError("Distance matrix must be square")

        if not 0 <= start_index < size:
            raise ValueError("Invalid start index")

        manager = pywrapcp.RoutingIndexManager(
            size,
            1,
            start_index,
        )

        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)

            return distance_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(
            distance_callback
        )

        routing.SetArcCostEvaluatorOfAllVehicles(
            transit_callback_index
        )

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()

        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        solution = routing.SolveWithParameters(search_parameters)

        if solution is None:
            raise ValueError("Unable to find a valid route")

        route = []
        total_distance = 0

        index = routing.Start(0)

        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))

            previous_index = index
            index = solution.Value(routing.NextVar(index))

            total_distance += routing.GetArcCostForVehicle(
                previous_index,
                index,
                0,
            )

        route.append(manager.IndexToNode(index))

        return {
            "route": route,
            "total_distance": total_distance,
        }


logistics_service = LogisticsService()