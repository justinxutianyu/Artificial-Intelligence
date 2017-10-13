"""
Python PDDL

Implements a class for interfacing between
generic Python objects and the PDDL planning
language.
"""

class PDDLPlan(object):

    def __init__(self, domain, problem):
        self.domain = domain
        self.problem = problem

class PDDLDomain(object) :
    

    def __init__(self, name, defi):
        self.name = name
        self.definition = defi

    # def add_predicate(self, predicate):
        # self.predicates.append(predicate)

    # def remove_predicate(self, predicate):
        # self.predicates.remove(predicate)

    # def add_action(self, action):
        # self.actions.append(action)

    # def remove_action(self, action):
        # self.actions.append(action)

    # def to_file(self, filename):
        # output = open(filename, 'w')
        # output.write("(define (domain {})\n".format(self.name))
        # output.write("\t(:requirements :strips)\n")
        # output.write("\t(:predicates\n")
        # for predicate in self.predicates:
            # output.write("\t\t{}\n".format(predicate.to_string()))
        # output.write("\t)\n")
        # for action in self.actions:
            # output.write("\t{}".format(action.to_string()))
        # output.write(")")
        
    def to_file(self, filename):
        output = open(filename, 'w')
        output.write(self.definition)

class PDDLProblem(object):

    def __init__(self, name, domain, objects, initial_state, goal_state):
        self.name = name
        self.domain = domain
        self.objects = objects
        self.initial_state = initial_state
        self.goal_state = goal_state

    def add_object(self, object):
        self.objects.append(object)

    def remove_object(self, object):
        self.objects.remove(object)
	
	def set_objects(self, objectList) :
		self.objects = objectList

    def set_initial_state(self, state):
        self.initial_state = state

    def set_goal_state(self, state):
        self.goal_state = state

    def to_file(self, filename):
        output = open(filename, 'w')
        output.write("(define (problem {})\n".format(self.name))
        output.write("\t(:domain {})".format(self.domain.name))
        output.write("\n\t(:objects ")
        for object in self.objects:
            output.write("{} ".format(object.to_string()))
        output.write(")")
        output.write("\n\t(:init ")
        for object in self.initial_state.list:
            output.write("{} \n\t\t".format(object.to_string()))
        output.write(")")
        output.write("\n\t(:goal (and ")
        for object in self.goal_state.list:
            output.write("{} \n\t\t".format(object.to_string()))
        output.write("))")
        output.write(")")
        output.close()

class PDDLAction(object):

    def __init__(self, name, parameters, precondition, effect):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect

    def set_precondition(self, state):
        self.precondition = state

    def set_effect(self, state):
        self.effect = state

    def to_string(self):
        base = "(:action {}\n\t\t:parameters (".format(self.name)
        for param in self.parameters:
            base += " ?{}".format(param)
        base += ")\n"
        base += "\t\t:precondition {}\n".format(self.precondition.to_string())
        base += "\t\t:effect {})".format(self.effect.to_string())
        return base

class PDDLObject(object):

    def __init__(self, name):
        self.name = name

    def to_string(self):
        return self.name

class PDDLState(object):

    def __init__(self, name, listP):
        self.name = name
        self.list = listP

    def to_string(self):
        string = ""
        for item in self.list :
            string = string + "(" + item.to_string() + ")\n"
        return string

class PDDLPredicate(object):

    def __init__(self, name, params):
        self.name = name
        self.params = params

    def to_string(self):
        base = "({}".format(self.name)
        for param in self.params:
            base += " {}".format(param)
        return base + ")"

def test_problem():
    domain = PDDLDomain("test-domain")
    problem = PDDLProblem("test-problem", domain)

    pred = PDDLPredicate("is-a-predicate", ["x"])
    init = PDDLState("and", [pred])
    goal = PDDLState("not", [pred])

    problem.objects.append(PDDLObject("an-object"))
    problem.set_initial_state(init)
    problem.set_goal_state(goal)

    problem.to_file("test_problem.pddl")

def test_domain():
    domain = PDDLDomain("test-domain")

    pred_x = PDDLPredicate("is-good", ["x"])
    pred_y = PDDLPredicate("is-bad", ["x", "y"])

    state_y = PDDLState("not", [pred_y])
    state_x = PDDLState("and", [pred_x, state_y])

    do_this = PDDLAction("do-this", ["x", "y"], state_y, state_x)
    #do_that = PDDLAction("do-that", ["x"])

    domain.add_predicate(pred_x)
    domain.add_predicate(pred_y)
    domain.add_action(do_this)

    domain.to_file("test.pddl")

if __name__ == "__main__":
    test_problem()
