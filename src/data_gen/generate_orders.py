import os, json, uuid, random, argparse
from datetime import datetime, timedelta
from faker import Faker
fake = Faker()
PRODUCTS = [{"id":"P-001","name":"T-Shirt","price":19.99},{"id":"P-002","name":"Sneakers","price":79.99}]
def generate_order(order_ts):
    order_id=str(uuid.uuid4()); items=[]; total=0.0
    num_items=random.choices([1,2],weights=[0.8,0.2])[0]
    for _ in range(num_items):
        p=random.choice(PRODUCTS); qty=1
        items.append({"product_id":p["id"],"name":p["name"],"qty":qty,"unit_price":p["price"]})
        total+=p["price"]*qty
    return {"order_id":order_id,"user_id":str(uuid.uuid4()),"email":fake.email(),"order_ts":order_ts.isoformat(),"event_date":order_ts.strftime("%Y-%m-%d"),"items":items,"total":round(total,2),"city":fake.city()}
def write_ndjson(out_dir,num,start,batch):
    os.makedirs(out_dir,exist_ok=True); written=0; current=start; idx=0
    while written<num:
        idx+=1; fname=os.path.join(out_dir,f"orders_{idx}.ndjson")
        with open(fname,"w") as f:
            for _ in range(min(batch,num-written)):
                f.write(json.dumps(generate_order(current))+"\n"); written+=1; current+=timedelta(seconds=random.randint(10,600))
        print("wrote",fname)
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',default='src/data_gen/output'); p.add_argument('--num',type=int,default=100); p.add_argument('--batch',type=int,default=50)
    args=p.parse_args(); write_ndjson(args.out,args.num,datetime.utcnow(),args.batch)
