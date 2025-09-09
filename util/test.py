from outbound import Outbound

out = Outbound(is_debug=False, is_server=False)

out.log(state="SERVER", context="This is an example of out.log")
out.warn(state="SERVER", context="This is an example of out.warn")
out.error(state="SERVER", context="This is an example of out.error")
out.success(state="SERVER", context="This is an example of out.success")

input()