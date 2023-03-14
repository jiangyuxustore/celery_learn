# from kombu import Queue, Exchange
#
#
# default_exchange = Exchange("default_exchange", type='direct')
# default_queue = Queue("default_queue", exchange=default_exchange, routing_key="default", durable=True, auto_delete=True,
#                       queue_arguments={'x-max-priority': 10, 'x-queue-type': 'classic'})
#
# topic_exchange = Exchange("topic_exchange", type="topic")
# topic_queue = Queue("topic_queue", exchange=topic_exchange, routing_key="user.#", bindings="user.#", durable=True, auto_delete=True,
#                     queue_arguments={'x-max-priority': 10, 'x-queue-type': 'classic', 'x-max-length': 2000000})
#
# quorum_queue = Queue("quorum_queue", exchange=topic_exchange, routing_key="blog.#", bindings="blog.#",
#                      queue_arguments={
#                          'x-queue-type': 'quorum',
#                          'x-max-length': 2000000,
#                          'x-overflow': 'reject_publish',
#                          'x-delivery-limit': 2,
#                          "x-queue-lead-locator": "balanced",
#                          # "x-dead-letter-exchange": "dead_letter_exchange",
#                          # "x-dead-letter-routing-key": "dead_letter_routing_key"
#                      })
