import ROOT as r

def showAvailableFits():

    import FitManager

    availablefits = FitManager.get_plugins(FitManager.FitProvider)
    print '-->> Available fit plugins : '
    for entry in availablefits:
        print entry
    print '<<--'
    print ' '

def showAvailableCorrs():

    import CorrectionManager

    availablecorrs = CorrectionManager.get_plugins(CorrectionManager.CorrectionProvider)
    print '-->> Available correction plugins : '
    for entry in availablecorrs:
        print entry
    print '<<--'
    print ' '

def setupDirStructure(dirName, Luminometer, Corr):

    import os

    baseDir = './'+dirName

    corrFull = ""
    for entry in Corr:
        corrFull = corrFull + '_' + str(entry)

    if corrFull[:1] == '_':
        corrFull = corrFull[1:]

    if  not corrFull:
        corrFull = "noCorr"

    dirList = [baseDir, baseDir+'/corr', baseDir+'/cond', baseDir+'/LuminometerData', baseDir+'/'+Luminometer, \
                   baseDir+'/'+Luminometer+'/graphs', baseDir+'/'+Luminometer+'/results', \
                   baseDir+'/'+Luminometer+'/results' + '/'+ corrFull] 

    print '-->> Make directories: '
    for entry in dirList:
        if not os.path.isdir(entry):
            print entry
            os.mkdir(entry, 0755 )
            
    print ' '


def makeCorrString(Corr):

    corrFull = ""
    for entry in Corr:
        corrFull = corrFull + '_' + str(entry)

    if corrFull[:1] == '_':
        corrFull = corrFull[1:]

    if  not corrFull:
        corrFull = "noCorr"

    return corrFull

def makeGraphs2D(GraphFile1D_X, GraphFile1D_Y):

    import os
    import pickle

    if not(os.path.isfile(GraphFile1D_X)):
        print "File with 1D X graphs doesn't exist, needs to be available before 2D graphs can be filled"
        sys.exit(1)
    if not(os.path.isfile(GraphFile1D_Y)):
        print "File with 1D Y graphs doesn't exist, needs to be available before 2D graphs can be filled"
        sys.exit(1)

    graphsX ={}
    graphsY ={}

    infile = open(GraphFile1D_X, 'rb')
    graphsX = pickle.load(infile)
    infile.close()

    infile = open(GraphFile1D_Y, 'rb')
    graphsY = pickle.load(infile)
    infile.close()

    if (len(graphsX) != len(graphsY)):
        print "Invalid X-Y scan pair, # of X-scan graphs, ' + len(graphsX) +', is different from # of Y-scan graphs, '+ len(graphsY)"
        sys.exit(1)

    graphs2D = {}

    for key in graphsX.keys():

        ndpX = graphsX[key].GetN()
        dpXx = graphsX[key].GetX()
        dpEXx = graphsX[key].GetEX()
        dpXy = graphsX[key].GetY()
        dpEXy = graphsX[key].GetEY()
    
        ndpY = graphsY[key].GetN()
        dpYx = graphsY[key].GetX()
        dpEYx = graphsY[key].GetEX()
        dpYy = graphsY[key].GetY()
        dpEYy = graphsY[key].GetEY()

        listX = [dpXx[i] for i in range(ndpX)]
        helperlist =[0.0 for i in range(ndpY)]
        listX.extend(helperlist)
        listEX = [dpEXx[i] for i in range(ndpX)]
        listEX.extend(helperlist)

        listY =[0.0 for i in range(ndpX)]
        helperlist = [dpYx[i] for i in range(ndpY)]
        listY.extend(helperlist)
        listEY =[0.0 for i in range(ndpX)]
        helperlist = [dpEYx[i] for i in range(ndpY)]
        listEY.extend(helperlist)
        
        listZ =[dpXy[i] for i in range(ndpX)]
        helperlist = [dpYy[i] for i in range(ndpY)]
        listZ.extend(helperlist)
        listEZ =[dpEXy[i] for i in range(ndpX)]
        helperlist = [dpEYy[i] for i in range(ndpY)]
        listEZ.extend(helperlist)
    
        import array
        aX = array.array("d",listX)
        aY = array.array("d",listY)
        aZ = array.array("d",listZ)
        aEX = array.array("d",listEX)
        aEY = array.array("d",listEY)
        aEZ = array.array("d",listEZ)
    
        name2D = "G2D"+str(key)
        g2D = r.TGraph2DErrors(ndpX+ndpY, aX, aY, aZ, aEX, aEY, aEZ, "")
        g2D.SetName(name2D)
        g2D.SetTitle(name2D)

        graphs2D[key] = g2D
        
    return graphs2D


def Residuals(g,ff):

    res=r.TGraphErrors()
	
    n=g.GetN()
    x=g.GetX()
    y=g.GetY()
    xe=g.GetEX()
    ye=g.GetEY()

    for i in range(n):
        val = ff.Eval(x[i])
        dev = (y[i]-val)/ye[i]
        res.SetPoint(i,x[i],dev)
        res.SetPointError(i,0,1)
        
    return res


def doPlot1D(graph,fList, fill): 

# fList is a list of functions that is returned by doFit() in xxx_Fit.py
# for 1D fit functions is usually the full fit function and a list of the various components, for example 
# for a DG plus const fit, the components are firstGauss, secondGauss, const
# for 2D fits, the fList usually has as first element the 1D projections of the 2D fit function

    r.gROOT.SetBatch()	
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    r.gStyle.SetOptFit(111)
    r.gStyle.SetOptStat(0)
    r.gStyle.SetTitleBorderSize(0)
    
    c = r.TCanvas("c","c",600,700)
    p1 = r.TPad('p1','p1',0,0,1,.25)
    p2 = r.TPad('p2','p2',0,.25,1,1)
    p2.SetBottomMargin(0)
    p1.SetTopMargin(0)
    p1.SetBottomMargin(0.2)
    p2.SetLogy()
    p2.Draw()
    p1.Draw()
    c.Update()
    
# Convention: first entry in list is full fit function, second to len-1 is the various signal components, last entry is background function    
    
    ff = fList[0]
    fComponent = {}
    for i in range(1,len(fList)):
        fComponent[i-1] = fList[i]

# Convention: Amplitude is called "Amp" in full fit function
    peak = ff.GetParameter("Amp")

# Convention: CapSigma, if it can be defined, is called "#Sigma"; if it is not defined for the fit function, root returns 1e-300 as value
    sigma = ff.GetParameter("#Sigma")
    m = ff.GetParNumber("#Sigma")
    sigmaE = ff.GetParError(m)

    title = graph.GetTitle()
    title_comps = title.split('_')
    scan = title_comps[0]
    type = title_comps[1]
    bcid = title_comps[2]
    print "graph title", title


# determine minimum rate in graph to set range of y axis for display 

    import array

    n = graph.GetN()
    y = array.array('d',[])
    y = graph.GetY()
    locmin = r.TMath.LocMin(n,y)
    minval = y[locmin]
    yval = []

    if minval<0.:
        print "Attention: Graph has negative rates for ", title 
        for i in range(n):
            yval.append(y[i])
        while minval < 0.:
            yval.remove(minval)
            minval =  min(yval)

    graph.SetTitle("Scan " + scan + ": " + type + "-plane BCID " + bcid)
    graph.GetYaxis().SetTitle("L / (N1*N2) [a.u.]")
    graph.GetYaxis().SetRangeUser(minval,10*peak)
    graph.GetXaxis().SetTitle("#Delta [mm]")
    graph.SetMarkerStyle(8)
    graph.GetYaxis().SetLabelFont(63)
    graph.GetYaxis().SetLabelSize(16)
    graph.GetYaxis().SetTitleFont(63)
    graph.GetYaxis().SetTitleSize(18)
    graph.GetYaxis().SetTitleOffset(1.5)
    graph.GetXaxis().SetNdivisions(0)

    res = Residuals(graph,ff)
    res.GetXaxis().SetLabelFont(63)
    res.GetXaxis().SetLabelSize(16)
    res.GetYaxis().SetLabelFont(63)
    res.GetYaxis().SetLabelSize(16)
    res.GetXaxis().SetTitleFont(63)
    res.GetXaxis().SetTitleSize(18)
    res.GetXaxis().SetTitleOffset(3)
    res.GetYaxis().SetTitleFont(63)
    res.GetYaxis().SetTitleSize(18)
    res.GetYaxis().SetTitleOffset(1.5)

    p2.cd()
    graph.Draw('AP')
    p2.Update()

#    print "STATS", graph.GetListOfFunctions().FindObject("stats")
#    print "STATS", graph.GetListOfFunctions().Print()


# this is the case for 2D fits, where the 1D projection of the 2D fit function is not associated to the 
# 1D projection of the original graph2D; when adding the function to the 1D graph, the parameters of the 
# 1D function as set in xx_2D_Fit.py are displayed in the stat box

#    if graph.GetListOfFunctions().Print("Q") == None:
    if graph.GetListOfFunctions().FindObject("stats") == None:
        graph.GetListOfFunctions().Add(ff)
                
    xmin = graph.GetXaxis().GetXmin()
    xmax = graph.GetXaxis().GetXmax()
        
    for i in range(len(fComponent)):
        fComponent[i].SetRange(xmin, xmax)
        fComponent[i].SetRange
        fComponent[i].SetLineColor(i+2)
        fComponent[i].Draw("sames")


    pad = r.TPaveText(0.15,0.75,0.35,0.88,"NDC")
    pad.SetTextAlign(12) # left alignment
    pad.SetTextSize(0.04)
    pad.SetFillColor(0)
    pad.AddText("CMS Preliminary")
    pad.AddText("VdM Scan: Fill "+str(fill))
    pad.Draw("same")
    c.Update()

    pad2 = r.TPaveText(0.4,0.2,0.6,0.3,"NDC")
    pad2.SetTextSize(0.04)
    pad2.SetFillColor(0)
    if ff.GetParNumber("#Sigma") > 0:
        pad2.AddText("#Sigma = "+str(round(1e3*sigma,3))+ "#pm" + str(round(1e3*sigmaE,3))+ "[#mum]")
        pad2.Draw("same")

    p2.Draw() 
    c.Update()

    p1.cd()
    res.SetMarkerStyle(8)
    res.GetXaxis().SetTitle("#Delta [mm]")
    res.GetYaxis().SetTitle("Residuals [#sigma]")
    res.Draw("AP")
    c.Update()
    p1.Update()

    try:
        c.SaveAs("./plotstmp/"+graph.GetName()+".ps")
    except ValueError:
        print "vdmUtilities: problem saving .ps file, maybe temporary directory to store pdf files not available"

    try:
        c.SaveAs("./plotstmp/"+graph.GetName()+".root")
    except ValueError:
        print "vdmUtilities: problem saving .root file, maybe temporary directory to store pdf files not available"


    return c


def doPlot2D(graph,fList, fill): 

    print "needs to be implemented"


def orderedIntKeysFirst(keylist):
    intlist = []
    stringlist = []
    for entry in keylist:
        try:
            intlist.append(int(entry))
        except ValueError:
            stringlist.append(entry)
    return sorted(intlist, key=int) + stringlist
