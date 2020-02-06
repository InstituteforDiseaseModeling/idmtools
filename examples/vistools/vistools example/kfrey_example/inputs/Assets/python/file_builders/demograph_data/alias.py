#********************************************************************************
#
# Alias table; DO NOT ALIAS TO AN ALIAS
#
# Python 3.6.0
#
#********************************************************************************

dataDic = \
  {'AFRO:NIGERIA:SOUTH':
       ['AFRO:NIGERIA:SOUTH_EAST'    ,
        'AFRO:NIGERIA:SOUTH_SOUTH'   ,
        'AFRO:NIGERIA:SOUTH_WEST'    ] ,

   'AFRO:DRCONGO:KATANGA_1997':
       ['AFRO:DRCONGO:TANGANYIKA'    ,
        'AFRO:DRCONGO:HAUT_LOMAMI'   ,
        'AFRO:DRCONGO:LUALABA'       ,
        'AFRO:DRCONGO:HAUT_KATANGA'  ] ,
   
   'AFRO:DRCONGO:KASAI_ORIENTAL_1997':
       ['AFRO:DRCONGO:LOMAMI'    ,
        'AFRO:DRCONGO:SANKURU'   ,
        'AFRO:DRCONGO:KASAI_ORIENTAL'] ,
   
   'AFRO:DRCONGO:KASAI_OCCIDENTAL_1997':
       ['AFRO:DRCONGO:KASAI_CENTRAL' ,
        'AFRO:DRCONGO:KASAI'         ] ,
   
   'AFRO:DRCONGO:KINSHASA_1997':
       ['AFRO:DRCONGO:KINSHASA'] ,
   
   'AFRO:DRCONGO:BAS_CONGO_1997':
       ['AFRO:DRCONGO:KONGO_CENTRAL' ] ,
   
   'AFRO:DRCONGO:BANDUNDU_1997':
       ['AFRO:DRCONGO:KWANGO'        ,
        'AFRO:DRCONGO:KWILU'         ,
        'AFRO:DRCONGO:MAI_NDOMBE'    ] ,
   
   'AFRO:DRCONGO:EQUATEUR_1997':
       ['AFRO:DRCONGO:EQUATEUR'      ,
        'AFRO:DRCONGO:TSHUAPA'       ,
        'AFRO:DRCONGO:MONGALA'       ,
        'AFRO:DRCONGO:NORD_UBANGI'   ,
        'AFRO:DRCONGO:SUD_UBANGI'    ] ,
   
   'AFRO:DRCONGO:ORIENTALE_1997':
       ['AFRO:DRCONGO:BAS_UELE'      ,
        'AFRO:DRCONGO:HAUT_UELE'     ,
        'AFRO:DRCONGO:ITURI'         ,
        'AFRO:DRCONGO:TSHOPO'        ] ,
   
   'AFRO:DRCONGO:MANIEMA_1997':
       ['AFRO:DRCONGO:MANIEMA'       ] ,

   'AFRO:DRCONGO:NORD_KIVU_1997':
       ['AFRO:DRCONGO:NORD_KIVU'     ] ,

   'AFRO:DRCONGO:SUD_KIVU_1997':
       ['AFRO:DRCONGO:SUD_KIVU'      ] ,
   
   '60CITY:SUBSET':
       ['60CITY:LIVERPOOL'           ,
        '60CITY:LONDON'              ,
        '60CITY:SHREWSBURY'          ,
        '60CITY:TEIGNMOUTH'          ,
        '60CITY:WOLVERHAMPTON'       ]
   
  }

#********************************************************************************

##from population import dataDic as popRef
##
##for val in dataDic:
##    for aval in dataDic[val]:
##        if(aval not in popRef):
##            print(aval)

#********************************************************************************
