
"""

TR:

Kütüphaneyi kullanmadan önce hspice programının path edildiğinden emin olunuz.

"""


import os , time , json , asyncio
import re
import subprocess


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print ('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
            
        return result
    return timed

class HSpicePy(object):
    """
    HSpicePy is a high-level wrapper for the HSpice simulator.
    It is designed to be used with the HSpicePy.py script.
    """

    def __init__(self, path :str,file_name : str,design_file_name : str,timeout :int , save_output : bool = True):
        """
        Initializes the HSpicePy class.
        path -> path of the .sp file
        file_name -> ".sp" file name
        design_file_name -> ".cir" file name
        timeout -> timeout of the simulation
        """
        self.file_name = file_name if ".sp" not in file_name else file_name[:-3]
        self.design_file_name = design_file_name if ".cir" not in design_file_name else design_file_name[:-4]
        self.path = path
        self.timeout = timeout
        self.parameters_dict = {}
        self.parameters = None
        self.instructions = []
        self.save_output = save_output
        self.__mt0_result = None
        self.__result = None
        self.__operation_point_result = None
    
    
    def set_parameters(self,**kwargs):
        """
        Sets the parameters of the HSpice simulation.
        """
        param = " "
        param = param.join(f"{key}={value}"for key,value in kwargs.items())
        param = ".PARAM " + param
        self.instructions.append(param)
        
    def get_parameters_from_cir(self): 
        """
        Gets the parameters from the cir file.

        
        TODO line ve alt satırlı
        """
        with open(f"{self.path}/{self.design_file_name}.cir","r") as file:
            data = file.read()
            params = re.findall(r'(?P<key>\w+)\s*=\s*(?P<value>[^ |\n]*)',data)
            file.close()
        parameters_dict = {}
        for key,value in params:
            parameters_dict[key] = value
        self.set_parameters(**parameters_dict)
    
    def change_parameters_to_cir(self,**kwargs):
        """
        Changes the parameters in the cir file.
        """
        params = ".PARAM\n"+"".join(f"+ {key} = {value}\n"for key,value in kwargs.items())
        with open(f"{self.path}\\{self.design_file_name}.cir","w+") as file:
            file.write(params)
            file.close()
    
    @property
    def result(self):
        """
        Returns the result of the simulation.
        """
        return self.__result
    
    @property
    def operation_point_result(self):
        """
        Returns the result of the simulation.
        """
        return self.__operation_point_result
    
    @property
    def mt0_result(self):
        """
        Returns the result of the simulation.
        """
        return self.__mt0_result


    # @result.setter
    # def result(self,value):
    #     self.__result = value
    
    # @result.deleter
    # def result(self):
    #     self.__result = None
    def __get_dp0_log(self):
        
        dp0_log = {}
        file_name = self.file_name + ".dp0"
        with open(f"{self.path}\\out\\{file_name}","r") as dp0:
            # data = dp0.read()
            tables = dp0.readlines()
            tables_ = {} 
            i = 0
            new_table = False
            table_number = 0
            for line in tables:
                line = line.replace("\n","")
                if line.startswith("-") and not new_table:
                    new_table = True
                    table_number += 1
                    table_line_number = 0
                    
                    continue
                if line.startswith("|-") and "+" not in line:
                    new_table = False

                if new_table:
                    if table_line_number == 0:
                        params = list(map(lambda x : x.strip(), list(filter(None, line.split("|")))))
                        
                        tables_[params[0]] = {key.strip() :{} for key in params[1:]}
                        
                    if table_line_number > 1:
                        variables = list(filter(None, line.split("|")))
                        variable_name = variables[0].strip()
                        variables = variables[1:]
                        i = 0
                        for key in params[1:]:
                            tables_[params[0]][key.strip()][variable_name] = variables[i].strip()
                            i+=0
                    table_line_number += 1
        if self.save_output:
            with open(f"{self.path}\\out\\{file_name[:-4]}_dp0.json","w") as outfile:
                json.dump(tables_, outfile)       
        self.__operation_point_result = tables_
        # print(tables_)            

    def __get_ma0_log(self):
        """
        TR
        -
        Simülasyon oluşturulduktan sonra oluşan .ma0 dosyasını okur ve çıktıları kaydeder.
        
        """
        file_name = self.file_name + ".ma0"
        with open(f"{self.path}\\out\\{file_name}","r") as ma0:
            # data = ma0.read()
            
            lines =  ma0.readlines()
        variables = lines[-2]
        results = lines[-1]
        res = {variable:result for variable,result in zip(variables.split(),results.split())}
        if self.save_output:
            with open(f"{self.path}\\out\\{file_name[:-3]}_ma0.json","w") as outfile:
                json.dump(res, outfile)
        self.__result = res

    def __get_mt0_log(self):
        """
        TR
        -
        Simülasyon oluşturulduktan sonra oluşan .mt0 dosyasını okur ve çıktıları kaydeder.
        
        """
        file_name = self.file_name + ".mt0"
        with open(f"{self.path}\\out\\{file_name}","r") as mt0:
            # data = ma0.read()
            
            lines =  mt0.readlines()
        variables = lines[-2]
        results = lines[-1]
        res = {variable:result for variable,result in zip(variables.split(),results.split())}
        if self.save_output:
            with open(f"{self.path}\\out\\{file_name[:-3]}_mt0.json","w") as outfile:
                json.dump(res, outfile)
        self.__mt0_result = res

    @timeit
    def run(self):
        try:
            file_name = self.file_name if ".sp" in self.file_name else self.file_name+".sp"
            os.makedirs(self.path+f"\\out", exist_ok=True) 
            subprocess.run([r'hspicerf', f"{self.path}\\{file_name}"],cwd=self.path+f"\\out")
            # os.system(f"hspicerf -ahv {self.path}//{file_name} {self.path}//output")   ,f" > "

            self.__get_ma0_log()
            self.__get_dp0_log()
            self.__get_mt0_log()
        except Exception as e:
            print(e)
            pass
        
    async def run_async(self):
        try:
            file_name = self.file_name if ".sp" in self.file_name else self.file_name+".sp"
            await asyncio.create_subprocess_shell(f"hspicerf {self.path}\\{file_name} {self.path}\\output",cwd=self.path+f"\\out")
            self.__get_ma0_log()
            self.__get_dp0_log()
        except Exception as e:
            print(e)
            pass     
        
        



meAbsPath = os.path.dirname(os.path.realpath(__file__))
h = HSpicePy(file_name="amp",design_file_name="designparam",path=meAbsPath,timeout="")

h.run()

print(h.result)
# h.change_parameters_to_cir(
#                             LM1=1.0092e-06,
#                             LM2 = 1.4842e-06,
#                             LM3 = 1.5565e-06,
#                             WM1 = 2.1734e-05,
#                             WM2 = 4.6268e-05,
#                             WM3 = 6.2646e-05,
#                             Rb = 10000,
#                             Vb = 0.55
#                             )
# asyncio.run(h.run_async())
# print(h.result)
# h.set_parameters(R1=1,R2=2,R3=3)


# # h.get_parameters_from_cir((meAbsPath +"\d.cir"))
# # print(h.parameters_dict)

