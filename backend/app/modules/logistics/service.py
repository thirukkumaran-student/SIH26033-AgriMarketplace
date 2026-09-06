from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


class LogisticsService:

    def optimize_route(
        self,
        distance_matrix: list[list[int]],
        start_index: int = 0,
    ) -> dict:

        if not distance_matrix:
            raise ValueError("Distance matrix cannot be empty.")

        size = len(distance_matrix)

        if any(len(row) != size for row in distance_matrix):
            raise ValueError(
                "Distance matrix must be square."
            )

        if not 0 <= start_index < size:
            raise ValueError(
                "Invalid start index."
            )

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

        solution = routing.SolveWithParameters(
            search_parameters
        )

        if solution is None:
            raise ValueError(
                "No feasible route found."
            )

        route = []
        total_distance = 0

        index = routing.Start(0)

        while not routing.IsEnd(index):

            node = manager.IndexToNode(index)
            route.append(node)

            previous_index = index

            index = solution.Value(
                routing.NextVar(index)
            )

            total_distance += routing.GetArcCostForVehicle(
                previous_index,
                index,
                0,
            )

        route.append(
            manager.IndexToNode(index)
        )

        return {
            "route": route,
            "total_distance": total_distance,
        }


logistics_service = LogisticsService()