
import argparse
import json
from src.services.product_service import p_s
from src.services.orders_service import o_s, OrderError
from src.services.payments_service import p_s as payments_service, PaymentError
from src.services.reports_service import r_s, ReportError
from src.dao.product_dao import p_d
from src.services.customers_service import c_s, CustomerError
 
def cmd_product_add(args):
    try:
        ps=p_s()
        p = ps.add_product(args.name, args.sku, args.price, args.stock, args.category)
        print("Created product:")
        print(json.dumps(p, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
 
def cmd_product_list(args):
    ps = p_s()
    products = ps.get_all_products()
    print(json.dumps(products, indent=2, default=str))
 
def cmd_customer_add(args):
    try:
        cs=c_s()
        c = cs.add_customer(args.name, args.email, args.phone, args.city)
        print("Created customer:")
        print(json.dumps(c, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
 
def cmd_order_create(args):
    items = []
    for item in args.item:
        try:
            pid, qty = item.split(":")
            items.append({"prod_id": int(pid), "qty": int(qty)})
        except Exception:
            print("Invalid item format:", item)
            return
    try:
        oss = o_s()
        ord = oss.create_order(args.customer, items)
        print("Order created:")
        print(json.dumps(ord, indent=2, default=str))
        
        # Automatically create a pending payment for the new order
        ps = payments_service()
        ps.add_pending_payment(ord['order_info']['order_id'], ord['order_info']['total_amount'])
        print("Pending payment created for the order.")
    except (OrderError, PaymentError) as e:
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
 
def cmd_order_show(args):
    try:
        oss = o_s()
        o = oss.get_order_details(args.order)
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
 
def cmd_order_cancel(args):
    try:
        oss = o_s()
        o = oss.cancel_order(args.order)
        print("Order cancelled (updated):")
        print(json.dumps(o, indent=2, default=str))
    except OrderError as e:
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
 
def cmd_payment_process(args):
    try:
        ps = payments_service()
        payment = ps.process_order_payment(args.order, args.method)
        print("Payment processed:")
        print(json.dumps(payment, indent=2, default=str))
    except PaymentError as e:
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
 
def cmd_report_top_products(args):
    try:
        rs = r_s()
        report = rs.get_top_selling_products()
        print("Top 5 Selling Products:")
        print(json.dumps(report, indent=2, default=str))
    except ReportError as e:
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
 
def cmd_report_monthly_revenue(args):
    try:
        rs = r_s()
        revenue = rs.get_monthly_revenue()
        print(f"Total revenue last month: {revenue}")
    except ReportError as e:
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
 
def cmd_report_customer_orders(args):
    try:
        rs = r_s()
        report = rs.get_total_orders_by_customer()
        print("Total orders by each customer:")
        print(json.dumps(report, indent=2, default=str))
    except ReportError as e:
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
 
def cmd_report_multiple_orders(args):
    try:
        rs = r_s()
        report = rs.get_customers_with_multiple_orders()
        print("Customers with more than 2 orders:")
        print(json.dumps(report, indent=2, default=str))
    except ReportError as e:
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
 
def build_parser():
    parser = argparse.ArgumentParser(prog="retail-cli")
    sub = parser.add_subparsers(dest="cmd")
 
    # product add/list
    p_prod = sub.add_parser("product", help="product commands")
    pprod_sub = p_prod.add_subparsers(dest="action")
    addp = pprod_sub.add_parser("add")
    addp.add_argument("--name", required=True)
    addp.add_argument("--sku", required=True)
    addp.add_argument("--price", type=float, required=True)
    addp.add_argument("--stock", type=int, default=0)
    addp.add_argument("--category", default=None)
    addp.set_defaults(func=cmd_product_add)
 
    listp = pprod_sub.add_parser("list")
    listp.set_defaults(func=cmd_product_list)
 
    # customer add
    pcust = sub.add_parser("customer")
    pcust_sub = pcust.add_subparsers(dest="action")
    addc = pcust_sub.add_parser("add")
    addc.add_argument("--name", required=True)
    addc.add_argument("--email", required=True)
    addc.add_argument("--phone", required=True)
    addc.add_argument("--city", default=None)
    addc.set_defaults(func=cmd_customer_add)
 
    # order
    porder = sub.add_parser("order")
    porder_sub = porder.add_subparsers(dest="action")
 
    createo = porder_sub.add_parser("create")
    createo.add_argument("--customer", type=int, required=True)
    createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
    createo.set_defaults(func=cmd_order_create)
 
    showo = porder_sub.add_parser("show")
    showo.add_argument("--order", type=int, required=True)
    showo.set_defaults(func=cmd_order_show)
 
    cano = porder_sub.add_parser("cancel")
    cano.add_argument("--order", type=int, required=True)
    cano.set_defaults(func=cmd_order_cancel)
 
    # payment
    ppay = sub.add_parser("payment")
    ppay_sub = ppay.add_subparsers(dest="action")
 
    processp = ppay_sub.add_parser("process")
    processp.add_argument("--order", type=int, required=True)
    processp.add_argument("--method", required=True, choices=['Cash', 'Card', 'UPI'])
    processp.set_defaults(func=cmd_payment_process)
 
    # report
    prep = sub.add_parser("report")
    prep_sub = prep.add_subparsers(dest="action")
 
    tpr = prep_sub.add_parser("top-products")
    tpr.set_defaults(func=cmd_report_top_products)
 
    mrv = prep_sub.add_parser("monthly-revenue")
    mrv.set_defaults(func=cmd_report_monthly_revenue)
 
    tco = prep_sub.add_parser("customer-orders")
    tco.set_defaults(func=cmd_report_customer_orders)
 
    cmo = prep_sub.add_parser("multiple-orders")
    cmo.set_defaults(func=cmd_report_multiple_orders)
 
    return parser
 
def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)
 
if __name__ == "__main__":
    main()