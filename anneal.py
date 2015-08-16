#!/usr/bin/env python
# encoding: utf-8
import subprocess, os, time, shutil, math, random
from signal import SIGKILL

def cost():
    pros = []
    p1 = None
    p2 = None
    try:
        os.remove(os.path.join('./bin/cost.txt'))
    except:
        pass
    try:
        kwargs = {'stdout':open('main_proc_log.txt','w'),
                  'stderr':open('main_proc_log.txt','a')}
        cmd = "./bin/start.py --offense-agents 3 --defense-npcs 2 " + \
              "--agent-on-ball --headless"
        cmd = os.path.join(cmd)
        p1 = subprocess.Popen(cmd.split(' '), shell=False, **kwargs)
        print 'Instance Launced'
        agentCmd = "./example/high_level_custom_agent.py 3"
        agentCmd = os.path.join(agentCmd)
        kwargs = {'stdout':open('agent_proc_log.txt','w'),
                  'stderr':open('agent_proc_log.txt','a')}

        p2 = subprocess.Popen(agentCmd.split(' '), shell=False, **kwargs)
        pros.append(p1)
        pros.append(p2)
        p1.communicate()
        try:
            with open(os.path.join('./bin/cost.txt'), 'r') as f:
                return float(f.readline().strip())
        except:
            return None
    except Exception as e:
        print e
        return None
    finally:
        try:
            p1.terminate()
            p1.kill()
        except:
            pass
        try:
            p2.terminate()
            p2.kill()
        except:
            pass

def neighbor():
    vals = []
    with open(os.path.join('./example/params.txt'), 'r') as f:
        for i in xrange(4):
            vals.append(float(f.readline().strip()))
    with open(os.path.join('./example/params.txt'), 'w') as f:
        for i in xrange(4):
            temp = vals[i] + random.gauss(0, 0.5)
            while temp > 1 or temp < -1:
                temp = vals[i] + random.gauss(0, 0.5)
            f.write(str(temp)+"\n")

def backup():
    shutil.copy2(os.path.join('./example/params.txt'),
                 os.path.join('./example/params_bak.txt'))

def replace():
    shutil.copy2(os.path.join('./example/params_bak.txt'),
                 os.path.join('./example/params.txt'))

def acceptance_probability(old_cost, new_cost, T):
    return math.exp((new_cost - old_cost)/T)

def anneal():
    old_cost = cost()
    while old_cost is None:
        old_cost = cost()
    T = 0.9
    T_min = 0.00001
    alpha = 0.9
    with open('anneal_log.txt', 'a') as f:
        f.write("T    i   new_cost    old_cost\n")
    while T > T_min:
        i = 1
        while i <= 20:
            backup()
            neighbor()
            new_cost = cost()
            while new_cost is None:
                new_cost = cost()
            print "T    i   new_cost    old_cost"
            print str(T)+"    "+str(i)+"    "+ \
                  str(new_cost)+"   "+str(old_cost)
            with open('anneal_log.txt', 'a') as f:
                f.write(str(T)+"    "+str(i)+"    "+ \
                  str(new_cost)+"   "+str(old_cost) + "\n" )
            if new_cost > old_cost:
                old_cost = new_cost
                with open(os.path.join('./example/params.txt'), 'r') as f:
                    params = f.read()
                with open('anneal_sol_log.txt', 'a') as f:
                    f.write("*******************\n")
                    f.write(params + '\n')
                    f.write("cost: " + str(new_cost) + "\n")
                    f.write("*******************\n")
            else:
                ap = acceptance_probability(old_cost, new_cost, T)
                if ap > random.random():
                    old_cost = new_cost
                else:
                    replace()
            i += 1
        T = T*alpha
    print "cost: " + str(old_cost)

if __name__ == '__main__':
  anneal()
